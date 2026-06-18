# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_obex.c

## Purpose
`f_obex.c` implements a USB CDC OBEX function for the composite gadget framework. It does not implement the OBEX protocol itself; it exposes a TTY-like byte stream over a CDC OBEX control/data interface pair and delegates stream handling to user space through the shared `u_serial` gadget layer. The function is marked `bind_deactivated`, so enumeration can be held off until the backing serial line is opened by the server that will handle the actual OBEX protocol.

## Important APIs, types, and functions
The central type is `struct f_obex`, which embeds `struct gserial port` and tracks dynamic control/data interface IDs, current alternate setting, and allocated serial port number. `obex_alloc_inst()` allocates a `struct f_serial_opts` instance and reserves a non-console gserial line through `gserial_alloc_line_no_console()`. `obex_alloc()` creates the USB function and wires callbacks for bind, unbind, alternate setting, disable, connect, and disconnect. Descriptor tables provide a CDC communication control interface, a CDC data interface with altsetting 0 as NOP and altsetting 1 with two bulk endpoints, plus full-speed and high-speed endpoint descriptors. Configfs exposes only a read-only `port_num` attribute.

`obex_bind()` assigns strings, reserves two interface numbers, patches the CDC union descriptor, autoconfigures IN and OUT bulk endpoints, mirrors endpoint addresses into high-speed descriptors, and calls `usb_assign_descriptors()`. `obex_set_alt()` validates control versus data interface requests, disconnects an existing gserial link on reset, configures endpoints by speed, and connects the gserial line only when the data interface is switched to altsetting 1. `obex_connect()` and `obex_disconnect()` call `usb_function_activate()` and `usb_function_deactivate()` so backing TTY readiness controls whether the function can be enumerated.

## Control flow
Configfs instance allocation reserves a serial line. Function allocation copies the reserved line number into `struct f_obex` and exposes composite callbacks. During bind, descriptors are patched with instance-specific interface IDs and endpoint addresses. At runtime, the host first selects the control interface altsetting 0, then the data interface. Data altsetting 0 leaves endpoints disconnected; altsetting 1 configures endpoints and calls `gserial_connect()`. Disable or a subsequent reset path calls `gserial_disconnect()`.

## State and persistence
Persistent state is limited to the lifetime of the function instance: reserved `port_num`, `ctrl_id`, `data_id`, `cur_alt`, endpoint descriptors, and the gserial port state. There is no on-disk persistence. Configfs state is read-only after line allocation. The function relies on `u_serial` for buffering, TTY lifetime, and wakeup behavior.

## Dependencies and integration points
The file depends directly on `u_serial.h`, the composite gadget core, configfs function registration, CDC descriptors from USB headers, and gadget controller altsetting support. `can_support_obex()` requires `gadget_is_altset_supported()` because the OBEX data interface uses alternate settings. Integration with user space occurs through the allocated `/dev/ttyGS*` line managed by `u_serial`.

## Risks and edge cases
The descriptor objects are file-static and patched during bind; multi-instance safety depends on the composite framework copying descriptors through `usb_assign_descriptors()`. Controllers without altsetting support cannot bind this function. If `config_ep_by_speed()` fails, endpoint descriptors are explicitly nulled to avoid stale descriptors. The activation/deactivation model can block enumeration if no user-mode OBEX server opens the serial backing line. The function has no OBEX-level validation, so protocol correctness and access control live entirely outside this file.

## Test signals
Useful tests include configfs creation of `functions/obex.*`, verification that `port_num` appears, binding failure on UDCs without altsetting support, descriptor inspection showing a CDC OBEX control interface and a two-altsetting CDC data interface, host switching altsetting 1 and observing `/dev/ttyGS*` traffic, and disconnect/reset paths proving `gserial_disconnect()` clears active transfers.
