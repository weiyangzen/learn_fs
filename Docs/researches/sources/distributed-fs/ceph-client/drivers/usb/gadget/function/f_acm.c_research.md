# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_acm.c

## Purpose
`f_acm.c` implements the USB CDC Abstract Control Model serial function. It wraps the generic gadget serial (`u_serial`) data path with CDC ACM descriptors, control requests for line coding and control line state, interrupt notifications for serial state, configfs attributes, and function registration under the name `acm`.

## Important APIs, Types, and Functions
`struct f_acm` embeds `struct gserial` and stores control/data interface IDs, port number, interface protocol, notification endpoint/request, line coding, handshake bits, serial state, and a spinlock protecting pending notifications. Descriptor tables cover FS/HS/SS, including IAD, control/data interfaces, CDC header/call-management/ACM/union descriptors, notify interrupt endpoint, and bulk data endpoints. Key functions are `acm_setup()`, `acm_complete_set_line_coding()`, `acm_set_alt()`, `acm_disable()`, `acm_cdc_notify()`, `acm_notify_serial_state()`, `acm_cdc_notify_complete()`, `acm_connect()`, `acm_disconnect()`, `acm_send_break()`, `acm_bind()`, `acm_unbind()`, `acm_alloc_instance()`, and `acm_alloc_func()`.

## Control Flow
Creating a configfs instance allocates `f_serial_opts`, reserves a `u_serial` line, and exposes `port_num`, `protocol`, and optional console attributes. Allocating a function creates `f_acm`, copies the selected port/protocol, and installs USB function callbacks. During bind, strings and interface IDs are assigned, endpoint addresses are autoconfigured for bulk IN/OUT and interrupt notify, a notification request is allocated, HS/SS descriptors inherit endpoint addresses, and descriptor copies are assigned. `set_alt()` enables the notify endpoint for the control interface and connects/disconnects the generic serial port on the data interface. `setup()` handles SET/GET_LINE_CODING, SET_CONTROL_LINE_STATE, and SEND_BREAK, queuing EP0 responses or OUT completions as needed.

## State and Persistence
Line coding defaults to the zeroed struct until the host sets it. `port_handshake_bits` records DTR/RTS-like state but data flow is not gated on DTR. `serial_state` is updated on connect/disconnect/break and sent through a single reusable notification request. If a serial-state change occurs while the request is in flight, `pending` causes the completion handler to send another notification. Instance state persists while the configfs function instance exists; concrete function state is freed by `free_func`.

## Dependencies and Integration Points
The file depends on `u_serial` for TTY allocation, connect/disconnect, suspend/resume, console helpers, and request allocation. It integrates with composite helpers for string IDs, interface IDs, endpoint autoconfig, speed-based endpoint configuration, and descriptor assignment. It registers with the function framework using `DECLARE_USB_FUNCTION_INIT(acm, ...)`.

## Risks
The notification path is interrupt/callback-sensitive and relies on `acm->lock` plus a single request. `SET_LINE_CODING` accepts and stores host data without semantic validation. Static descriptor templates are patched at bind time before per-instance copies; multi-instance behavior depends on prompt copying after patching. The SS descriptor table reuses the HS notify descriptor plus an SS companion descriptor, so endpoint companion ordering must match composite expectations. DTR is recorded but not enforced, which may surprise hosts or tests expecting no data before DTR.

## Test Signals
Enumerate ACM at FS/HS/SS, open/close `/dev/ttyGS*`, issue CDC line coding/control line state/break requests, verify interrupt SerialState notifications and pending notification replay, suspend/resume serial traffic, create multiple ACM instances with different protocols, and test configfs protocol writes fail with `-EBUSY` while instances exist.
