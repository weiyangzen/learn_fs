# Research group subset-b-005493

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_obex.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_obex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_phonet.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_phonet.c

## Purpose
`f_phonet.c` implements a USB CDC Phonet gadget function. It exposes a Linux Phonet network device backed by a USB CDC control/data interface pair, translating between USB bulk transfers and `ETH_P_PHONET` socket buffers. The function is specialized for Nokia/Phonet-style point-to-point networking rather than Ethernet framing.

## Important APIs, types, and functions
`struct f_phonet` embeds `struct usb_function`, holds IN/OUT bulk endpoints, one reusable transmit request, an array of receive requests sized by `phonet_rxq_size`, and a receive-fragment accumulator. `struct phonet_port` is the netdev private area and contains a backpointer to the active USB function guarded by a spinlock. `pn_net_setup()` configures the netdev as `ARPHRD_PHONET`, point-to-point, no-ARP, one-byte hardware address with media value `PN_MEDIA_USB`, Phonet MTU limits, and `phonet_header_ops`.

The netdev entry points are `pn_net_open()`, `pn_net_close()`, and `pn_net_xmit()`. TX validates `skb->protocol == ETH_P_PHONET`, queues the skb data on the USB IN request, stops the net queue, and resumes it in `pn_tx_complete()`. RX is driven by `pn_rx_submit()` and `pn_rx_complete()`, which allocate page-sized USB buffers, assemble multi-fragment Phonet frames into an skb, and deliver complete frames through `netif_rx()`. `pn_set_alt()`, `pn_get_alt()`, and `pn_disconnect()` handle USB activation and reset.

## Control flow
`phonet_alloc_inst()` allocates the configfs instance and default netdev via `gphonet_setup_default()`. `phonet_alloc()` creates a function object with flexible storage for RX requests. `pn_bind()` registers the netdev once, reserves control and data interfaces, autoconfigures bulk endpoints, assigns descriptors, allocates the RX request array and TX request, and leaves the carrier off. When the host selects data altsetting 1, `pn_set_alt()` configures and enables endpoints, installs endpoint driver data, sets `port->usb`, raises carrier, and queues the RX request pool. TX packets can then flow from the Phonet netdev to USB IN. OUT completions resubmit receive requests until disconnect or endpoint reset statuses stop resubmission.

## State and persistence
State persists only in kernel memory: the registered netdev, active `port->usb` pointer, carrier state, endpoint enablement, pending RX pages, in-flight TX skb, and current fragmented RX skb. `phonet_opts->bound` records whether the netdev was registered so instance teardown chooses `gphonet_cleanup()` versus `free_netdev()`. No file or firmware state is stored.

## Dependencies and integration points
The driver integrates with the network stack (`struct net_device`, `netif_rx`, stats, carrier state), the Phonet stack (`linux/if_phonet.h`, `phonet_header_ops`), the USB composite framework, and CDC descriptors. It shares some helper naming with `u_ether` for netdev ifname exposure but uses Phonet-specific framing. Configfs exposes a read-only `ifname` attribute.

## Risks and edge cases
`MAXPACKET` must divide `PAGE_SIZE`, enforced at compile time, because RX pages are accumulated as USB fragments. RX can drop frames if `MAX_SKB_FRAGS` is exceeded or if skb allocation fails. TX uses a single request and a one-entry netdev queue, so throughput is intentionally constrained. The code assumes bind ordering avoids races around `phonet_opts->bound`. Locking is split between the netdev private spinlock and `fp->rx.lock`; reset paths must clear `fp->rx.skb` and disable endpoints while TX/RX callbacks may still complete. Host altsetting 0 leaves the netdev registered but carrier-off.

## Test signals
Tests should create the Phonet function, confirm the `upnlink%d` interface and read-only `ifname`, inspect descriptors for the CDC Phonet control/data interfaces and altsetting 1 data endpoints, bring the netdev up/down, transmit non-Phonet and Phonet skbs to validate drop and queue behavior, stress fragmented OUT transfers including short final packets, and verify disconnect/reset stops resubmission and clears carrier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_phonet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_printer.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_printer.c

## Purpose
`f_printer.c` implements a USB printer class function with a userspace-facing character device. It presents a bidirectional printer interface to the USB host while exposing `/dev/g_printerN` for a local printer emulation or forwarding process. It is derived from the legacy printer gadget but packaged as a configfs USB function.

## Important APIs, types, and functions
`struct printer_dev` is the core object. It contains endpoint pointers, a `struct cdev`, minor number, kref, printer status bits, reset flag, interface number, request queues for free/active/completed RX and TX transfers, waitqueues for read/write/flush, a current partially consumed RX request, queue length, and a pointer to the configfs PNP string. Static descriptors define one USB printer interface with full-, high-, and super-speed bulk IN/OUT endpoints.

Character-device operations are `printer_open()`, `printer_close()`, `printer_read()`, `printer_write()`, `printer_fsync()`, `printer_poll()`, and `printer_ioctl()`. USB completion paths are `rx_complete()` and `tx_complete()`. Interface lifecycle is handled by `set_printer_interface()`, `printer_reset_interface()`, `set_interface()`, and `printer_soft_reset()`. EP0 class handling uses `gprinter_req_match()` and `printer_func_setup()` for `GET_DEVICE_ID`, `GET_PORT_STATUS`, and `SOFT_RESET`. Configfs exposes `pnp_string` and `q_len`, with `q_len` rejected after functions reference the instance.

## Control flow
`gprinter_alloc_inst()` initializes the global printer class and chrdev region on the first instance, allocates an IDA minor, and stores defaults. `gprinter_alloc()` creates `printer_dev`, initializes lists and waitqueues, copies the minor, PNP string pointer, and queue length, then installs USB callbacks. `printer_func_bind()` reserves the interface ID and endpoints, assigns descriptors, allocates `q_len` TX and RX USB requests, creates the device node, and registers the `cdev`. `printer_func_set_alt()` enables endpoints for altsetting 0. Local reads queue RX requests, sleep until completed buffers appear, copy OUT data to user memory, and recycle requests. Local writes copy user data into free TX requests and queue them to the IN endpoint. Completion callbacks move requests back to free or completed lists and wake blocked users.

## State and persistence
The function has substantial volatile state: request ownership across free, active, and completed lists; open/closed state; current RX cursor; printer status bits; reset flag; registered minor; and interface enabled state. Global state includes the printer class, major/minor allocation, and IDA pool protected by `printer_ida_lock`. Configfs settings persist for the instance lifetime but not across unload. The PNP string memory is owned by options when allocated through configfs; `printer_dev` only holds a pointer-to-pointer so updates are visible.

## Dependencies and integration points
The file integrates with USB composite, endpoint request allocation, Linux char devices, sysfs device creation, poll/waitqueue semantics, copy-to/from-user, IDA minor allocation, and printer class requests from `linux/usb/g_printer.h`. Userspace consumes and produces printer data via `/dev/g_printerN`; the host consumes the USB printer class interface.

## Risks and edge cases
Concurrency is complex: a spinlock protects queues and flags, while `lock_printer_io` serializes file read/write/poll setup. Blocking waits must handle disconnects, resets, and nonblocking flags. `printer_soft_reset()` disables and reenables endpoints and recycles queues; the loop intended to drain `rx_reqs_active` references `dev->rx_buffers.next`, which is a high-risk area if active RX is nonempty. `printer_open()` calls `kref_get()` even when returning `-EBUSY`, which deserves scrutiny because failed opens should not usually acquire a reference. Partial `copy_from_user()` returns current progress without requeueing under all paths. Descriptor and class globals are shared across instances, so multi-instance behavior depends on careful bind ordering and static descriptor copying.

## Test signals
Tests should cover configfs instance creation, `pnp_string` and `q_len` behavior before and after allocation, device node creation for up to `PRINTER_MINORS`, exclusive open behavior, blocking and nonblocking reads/writes, `poll()` readiness, `fsync()` waiting for active TX completion, `GADGET_GET_PRINTER_STATUS` and `GADGET_SET_PRINTER_STATUS`, host `GET_DEVICE_ID`, `GET_PORT_STATUS`, and `SOFT_RESET`, disconnect while user I/O blocks, and request-list leak checks at unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_printer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_rndis.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_rndis.c

## Purpose
`f_rndis.c` implements the USB gadget RNDIS Ethernet function. It wraps the shared `u_ether` network transport with RNDIS packet framing, CDC ACM-style control descriptors, RNDIS RPC handling over CDC encapsulated commands, and optional Microsoft OS descriptor integration.

## Important APIs, types, and functions
`struct f_rndis` embeds `struct gether port` and tracks control/data interface IDs, host MAC address, vendor metadata, `struct rndis_params`, an interrupt notification endpoint, notification request, and atomic notification count. Descriptor tables define a control interface with CDC header/call-management/ACM/union descriptors, a data interface with bulk endpoints, an IAD, a status interrupt endpoint, and speed-specific full/high/super-speed variants.

Data framing is implemented by `rndis_add_header()` and `rndis_rm_hdr` from `rndis.h`. Control flow uses `rndis_setup()` to accept `USB_CDC_SEND_ENCAPSULATED_COMMAND`, parse commands later in `rndis_command_complete()`, and return queued responses for `USB_CDC_GET_ENCAPSULATED_RESPONSE`. `rndis_response_available()` and `rndis_response_complete()` manage the interrupt notification that tells the host to fetch responses. `rndis_set_alt()` configures the notification endpoint and data endpoints, connects `gether`, initializes `rndis_params` with the netdev and packet filter pointer, and starts with `cdc_filter = 0` until RNDIS initialization enables traffic. `rndis_open()` and `rndis_close()` signal medium connect/disconnect to the RNDIS engine.

## Control flow
`rndis_alloc_inst()` allocates Ethernet options, default netdev, configfs attributes, and an OS descriptor group. `rndis_alloc()` creates a function object, copies host MAC/vendor fields, installs RNDIS wrap/unwrap hooks, and registers an RNDIS parameter block with `rndis_register()`. `rndis_bind()` may register or attach the netdev, patches class/subclass/protocol fields from configfs, assigns strings and interface IDs, autoconfigures IN/OUT/notify endpoints, allocates the notify request, assigns descriptors, initializes RNDIS medium/host MAC/vendor state, and installs OS descriptor table entries if enabled. Runtime setup requests carry the RNDIS control protocol, while alternate setting activation enables endpoints and connects the Ethernet transport.

## State and persistence
State includes the `gether` network device, RNDIS parameter state machine, packet filter, notification count, endpoint descriptors, optional borrowed netdev, bind/ref counts in `f_rndis_opts`, OS descriptor storage, and configfs class/subclass/protocol/MAC/qmult/ifname attributes. No state persists beyond kernel object lifetime. `rndis_borrow_net()` can replace the owned default netdev with an externally supplied one.

## Dependencies and integration points
The driver integrates with `u_ether`, `u_ether_configfs`, `u_rndis`, RNDIS core helpers, configfs, Microsoft OS descriptors, the Linux netdev stack, and USB composite endpoint/control request handling. Host interoperability depends on RNDIS behavior expected by Windows and other RNDIS hosts, including interrupt response notifications and CDC encapsulated command transport.

## Risks and edge cases
RNDIS is protocol-fragile by design: control requests can be underspecified, hosts may expect nonstandard behavior, and traffic must not flow until the RNDIS packet filter is configured. `notify_count` coalesces multiple response notifications and must stay consistent across queue failures, reset, and shutdown. The function uses static descriptors patched per bind; multi-instance use depends on descriptor copying. `rndis_bind()` mixes lock-protected netdev registration with later descriptor setup, so cleanup paths must avoid detaching borrowed netdevs. Notification request memory and OS descriptor table ownership are split across bind/unbind and free paths. RNDIS expects early endpoint activation even before data is logically initialized, which can hide ordering bugs.

## Test signals
Tests should verify configfs attributes for MACs, qmult, ifname, class/subclass/protocol, OS descriptor exposure when `use_os_string` is active, descriptor layout with IAD/control/data interfaces and notify endpoint, CDC encapsulated command/response exchange, repeated response notifications, packet filter transitions from no traffic to active traffic, netdev registration and borrowed-net behavior, suspend/disconnect disable paths, and host interoperability with Windows/Linux RNDIS drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_rndis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_serial.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_serial.c

## Purpose
`f_serial.c` implements the generic USB serial gadget function. It exposes a vendor-specific interface with two bulk endpoints and connects it to the shared `u_serial` TTY backend. Unlike CDC ACM, it has no standardized control model; it is a raw byte pipe for hosts with matching drivers.

## Important APIs, types, and functions
`struct f_gser` embeds `struct gserial port` and stores the dynamic interface ID and allocated gserial line number. Static descriptor sets provide one vendor-specific interface and bulk IN/OUT endpoints for full, high, and super speed, including super-speed companion descriptors. `gser_alloc_inst()` allocates `struct f_serial_opts` and reserves a gserial line through `gserial_alloc_line()`. Configfs exposes read-only `port_num` and, when `CONFIG_U_SERIAL_CONSOLE` is enabled, a writable `console` attribute using `gserial_set_console()` and `gserial_get_console()`.

`gser_bind()` allocates a string ID, reserves the interface ID, autoconfigures endpoints, mirrors endpoint addresses to high/super-speed descriptors, and assigns descriptors. `gser_set_alt()` treats altsetting 0 as activation or reset: it disconnects an already enabled port, configures endpoints by speed, and calls `gserial_connect()`. `gser_disable()` and `gser_unbind()` disconnect the port, with unbind also freeing descriptors. `gser_suspend()`, `gser_resume()`, and `gser_get_status()` pass function suspend/resume and remote-wakeup capability state into `u_serial`.

## Control flow
Instance allocation reserves a TTY line. Function allocation copies the line number and installs callbacks. Bind patches descriptors and chooses endpoints. When the host selects the interface, `set_alt` configures the endpoints and attaches the gserial port to `ttyGS<port_num>`. Disable, unbind, or reset disconnects the port so pending TTY I/O sees carrier loss through the shared serial layer.

## State and persistence
State is intentionally small: endpoint descriptors, interface ID, port number, gserial connection state, and optional console setting managed by `u_serial`. There is no protocol state and no persistent storage. The function object owns only its `struct f_gser`; the instance owns the reserved serial line until `gser_free_inst()` calls `gserial_free_line()`.

## Dependencies and integration points
The function depends on USB composite APIs, configfs function instances, and `u_serial`. Host integration requires a vendor-specific driver or userspace configuration that knows how to bind to the interface. Kernel integration includes optional USB serial console support and function remote-wakeup status reporting.

## Risks and edge cases
Because the interface is vendor-specific, interoperability is weaker than CDC ACM. The string ID and descriptor objects are static and patched at bind time, so multi-instance correctness relies on descriptor copy behavior. `gser_set_alt()` assumes altsetting 0; unexpected alt values are not explicitly rejected in this function. Endpoint configuration failures clear descriptors before returning `-EINVAL`. Console mode can change how the reserved line is used and needs tests under `CONFIG_U_SERIAL_CONSOLE`.

## Test signals
Tests should create `functions/gser.*`, verify `port_num`, optionally exercise `console`, inspect descriptors across full/high/super speed, switch the host interface on and confirm `/dev/ttyGS*` traffic, test reset by repeated `set_alt`, and confirm disconnect/unbind wake or fail pending TTY operations without leaking the reserved line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_sourcesink.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_sourcesink.c

## Purpose
`f_sourcesink.c` implements the source/sink USB gadget test function used by the zero gadget family. It continuously sources data to the host on IN endpoints and sinks data from the host on OUT endpoints, with optional data-pattern validation and optional isochronous endpoints. Its primary purpose is USB controller, endpoint, throughput, and compliance testing.

## Important APIs, types, and functions
`struct f_sourcesink` embeds `struct usb_function` and stores bulk and isochronous endpoints, current alternate setting, pattern mode, isochronous interval/maxpacket/mult/maxburst, bulk buffer length, bulk maxburst, and queue depths. Descriptor tables expose altsetting 0 with two bulk endpoints and altsetting 1 with two bulk plus two isochronous endpoints when the UDC can autoconfigure isoch endpoints. Full-, high-, and super-speed descriptors are patched from configfs options.

`sourcesink_bind()` allocates the interface ID, clamps burst/interval values, autoconfigures bulk and optional iso endpoints, patches endpoint addresses and companion descriptors, disables altsetting 1 descriptors if iso endpoints are unavailable, and assigns descriptors. `check_read_data()` validates OUT buffers against all-zero or mod63 patterns, while pattern 2 disables validation. `reinit_write_data()` fills IN buffers. `source_sink_complete()` validates OUT completions, refills IN data when needed, and resubmits requests until shutdown or fatal queue error. `source_sink_start_ep()` allocates and queues `bulk_qlen` or `iso_qlen` requests. `enable_source_sink()` and `disable_source_sink()` manage endpoint enablement for selected altsetting. `sourcesink_setup()` implements vendor-specific control write/read tests `0x5b` and `0x5c`.

## Control flow
Configfs instance allocation initializes defaults from `g_zero.h`. Function allocation copies options into the function object, freezing settings while `refcnt` is nonzero. Bind prepares descriptors and endpoints. Each `set_alt` first disables active endpoints, then enables bulk endpoints, queues IN and OUT bulk requests, and, for altsetting 1, enables and queues iso endpoints if present. Completion callbacks recycle requests by immediately requeueing them, creating continuous traffic. Disable tears down endpoints; `free_func` decrements the options refcount and frees descriptors.

## State and persistence
State consists of copied configfs options, selected altsetting, endpoint enablement, and in-flight USB requests. No user data is retained except the shared ep0 buffer used by the control write/read test. Options live in `struct f_ss_opts` and are mutable only while no function references the instance. There is no persistent storage.

## Dependencies and integration points
The file depends on USB composite, `linux/usb/func_utils.h` allocation helpers, and `g_zero.h` defaults plus `lb_modinit()`/`lb_modexit()` for the loopback companion function. It registers `SourceSink` manually in module init and initializes loopback support in the same module. It integrates with host-side USB test tools, including control transfer tests modeled after USB compliance devices.

## Risks and edge cases
The function intentionally stresses controllers. Bad pattern data halts the OUT endpoint. Queue allocation failures during startup can leave a partially enabled endpoint stack that must unwind correctly. Optional iso endpoint absence mutates descriptor arrays by nulling altsetting 1 offsets, affecting the advertised interface. Configfs accepts zero queue lengths and buffer lengths where the resulting behavior should be understood by tests. Control request `0x5b` leaves data in the shared ep0 buffer for `0x5c`, so intervening control transfers could overwrite it. Continuous requeueing can amplify UDC DMA, SG, or shutdown races.

## Test signals
Tests should validate descriptor sets for altsetting 0 and optional altsetting 1, configfs rejection of invalid pattern/mult/burst/packet values while allowing changes before use, bulk and iso traffic at full/high/super speed, pattern modes 0, 1, and 2, endpoint halt on corrupted OUT data, vendor control write/read loopback, disable while requests are active, UDCs with and without isochronous endpoints, and module init/exit registering both SourceSink and loopback functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_sourcesink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_subset.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_subset.c

## Purpose
`f_subset.c` implements the CDC Ethernet Subset/SAFE gadget function. It exposes a simple two-bulk-endpoint Ethernet-like link through the shared `u_ether` layer, using descriptors that allow host drivers to recognize legacy CDC Subset or MCCI SAFE-style devices.

## Important APIs, types, and functions
`struct f_gether` embeds `struct gether port` and stores a CDC-format host Ethernet address string. Static descriptors define a single communication-class MDLM interface with CDC header, MDLM, MDLM detail, and CDC Ethernet descriptors, plus full/high/super-speed bulk endpoints. Configfs attributes are generated by `USB_ETHERNET_CONFIGFS_ITEM*` macros for device MAC, host MAC, qmult, and ifname.

`geth_alloc_inst()` allocates `struct f_gether_opts`, initializes its lock, and creates a default netdev through `gether_setup_default()`. `geth_alloc()` obtains the host address in CDC string format, stores it in the function-specific string descriptor, points `port.ioport` at the netdev private area, sets the default CDC packet filter, and installs callbacks. `geth_bind()` registers or attaches the netdev if needed, assigns strings and interface ID, autoconfigures endpoints, patches endpoint addresses, assigns descriptors, increments `bind_count`, and retains the netdev gadget attachment. `geth_set_alt()` configures endpoints and calls `gether_connect()`. `geth_disable()` disconnects the link.

## Control flow
The configfs instance owns the netdev. Allocating a function increments `refcnt` and binds the function object to that netdev. Binding ensures the netdev is registered or attached to the current gadget, patches the descriptors, and prepares endpoints. Host selection of altsetting 0 activates the bulk endpoints and connects the `gether` data path. Disable or reset disconnects the net path. Unbind frees descriptors, decrements `bind_count`, and detaches the gadget when no unbound function still needs it.

## State and persistence
State includes configfs Ethernet options, netdev registration/attachment, bind and reference counts, endpoint descriptors, CDC filter, and the generated host MAC string. No state is persisted beyond the function instance. The netdev is cleaned up with `gether_cleanup()` if registered, otherwise `free_netdev()`.

## Dependencies and integration points
The driver depends on `u_ether`, `u_ether_configfs`, `u_gether`, Linux Ethernet helpers, and USB composite descriptors. Host integration is through CDC Subset/SAFE-compatible drivers rather than full CDC ECM or RNDIS. It shares the same `gether` data-plane API used by other Ethernet gadget functions.

## Risks and edge cases
The function is intentionally nonstandard and may need specific host IDs or class matching. Static descriptor and string state is patched per bind, so multiple simultaneous instances require caution. Locking around `bind_count`, `bound`, and `refcnt` is important because netdev lifetime is shared across functions. `geth_string_defs[1].s` points at per-function `ethaddr`, so descriptor copy timing matters. The implementation has no control endpoint model for link management; it relies on raw bulk data and the shared `gether` layer.

## Test signals
Tests should create `functions/geth.*`, configure MAC addresses and qmult, verify `ifname`, bind to a UDC and inspect MDLM/SAFE plus Ethernet descriptors, confirm host driver binding, pass Ethernet frames over the `gether` netdev, reset via repeated interface selection, exercise multi-bind/refcount behavior, and check cleanup for registered versus never-registered netdevs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_subset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_tcm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_tcm.c

## Purpose
`f_tcm.c` implements the target-core-backed USB mass-storage gadget function. It supports both Bulk-Only Transport (BOT/BBB) and USB Attached SCSI (UAS/UASP), maps USB command and data phases into Linux target core `se_cmd` operations, and exposes a `usb_gadget` target fabric through target configfs. It is the bridge between USB gadget endpoints and TCM LUN/session management.

## Important APIs, types, and functions
The USB function object is `struct f_uas` from `tcm.h`, with endpoints for data IN/OUT, UAS command/status, BOT command/status requests, stream resources, a stream hash for active UAS tags, and a pointer to `struct usbg_tpg`. Target-side objects are `struct usbg_tport`, `struct usbg_tpg`, `struct tcm_usbg_nexus`, and `struct usbg_cmd`. `struct f_tcm_opts` in `u_tcm.h` controls function-instance dependency and attach callbacks.

BOT handling includes `bot_enqueue_cmd_cbw()`, `bot_cmd_complete()`, `bot_submit_command()`, `bot_send_read_response()`, `bot_send_write_request()`, `bot_send_status_response()`, and cleanup/setup helpers. UASP handling includes `uasp_cmd_complete()`, `usbg_submit_command()`, `uasp_send_read_response()`, `uasp_send_write_request()`, `uasp_send_status_response()`, `uasp_send_tm_response()`, `uasp_status_data_cmpl()`, stream allocation, and overlap-tag handling. Target fabric integration is defined by `usbg_ops`, with callbacks for fabric WWN/TPG creation, nexus management, command release, data-in/data-out/status, task management response, aborts, LUN link/unlink, and TPG enablement. Gadget descriptors expose altsetting 0 as BOT with two bulk endpoints and altsetting 1 as UAS with bulk data, status, and command pipes plus super-speed stream companions.

## Control flow
Module init registers the USB function and target fabric template. Configfs function instance allocation reserves one global TPG slot (`TPG_INSTANCES` is 1) and initializes dependency callbacks. Target configfs creates a WWN, then `tpgt_N`; `usbg_make_tpg()` binds that TPG to the reserved function instance, creates a workqueue, registers the target portal group, and takes a module or configfs dependency. The `nexus` attribute creates a target session with `USB_G_DEFAULT_SESSION_TAGS` command slots. Enabling the TPG calls `usbg_attach()`, which marks the USB function attachable.

On USB bind, `tcm_bind()` verifies `can_attach`, assigns one interface ID for both altsettings, autoconfigures four endpoints, patches full/high/super-speed descriptors, and assigns descriptors. `tcm_set_alt()` schedules delayed work and returns `USB_GADGET_DELAYED_STATUS`; the work tears down any old protocol, then calls `bot_set_alt()` or `uasp_set_alt()`. BOT queues a CBW request on OUT, converts valid CBWs into `usbg_cmd`, submits SCSI work to target core, then sends data and CSW. UASP queues command requests, parses command or task-management IUs, detects overlapping tags, maps priority attributes, submits to target core, and performs ready/data/status phases through the appropriate UAS endpoint or streams.

## State and persistence
State is volatile but layered: global `tpg_instances` links at most one function instance to one TPG; `f_tcm_opts` tracks ready/can_attach/dependency state; `usbg_tpg` tracks nexus, workqueue, LUN count, and gadget connection; target sessions own the command map and tag bitmap; `f_uas` tracks active protocol flags and endpoint/request resources; `usbg_cmd` tracks command CDB, LUN, data direction/length, tag, task-management state, temporary bounce buffer, and target `se_cmd`. Configfs target layout and function instances define runtime configuration but no file-backed state is written by this driver.

## Dependencies and integration points
The file integrates with USB composite, USB storage and UAS protocol definitions, Linux target core fabric APIs, SCSI command constants, configfs dependencies, workqueues, scatter-gather capable gadget endpoints, and optional super-speed streams. It exports the `usb_gadget` target fabric name and cooperates with target core LUN and ACL machinery. It also interacts with gadget registration callbacks so a target TPG can trigger composite attach/detach.

## Risks and edge cases
This is high-risk code because it combines USB completion context, workqueues, target-core lifetime rules, endpoint dequeue/disable, and configfs object dependencies. Only one TPG instance is supported, so parallel configurations can fail with `-EBUSY`. Missing nexus causes commands to be ignored or rejected. `get_cmd_dir()` is a hard-coded opcode classifier; unknown opcodes receive check condition and warnings, and new SCSI opcodes need updates. UASP overlap handling waits briefly for active stream completion to avoid false positives, then aborts active transfers; races here affect correctness under misbehaving hosts. Non-SG controllers allocate bounce buffers that must be freed in `usbg_release_cmd()`. BOT phase-error handling wedges and clears endpoints. TPG nexus removal is refused while LUN ports are linked. Delayed altsetting setup must call `usb_composite_setup_continue()` exactly after protocol setup.

## Test signals
Tests should cover target configfs WWN validation (`naa.` prefix), TPG creation limit, nexus create/drop including active LUN refusal, TPG enable/disable invoking attach/detach, descriptor inspection for BOT and UAS altsettings at all speeds, BOT reset and max-LUN requests, valid and invalid CBWs, BOT read/write/status and phase errors, UASP command and task-management IUs, overlapping tag behavior, super-speed stream and non-stream paths, SG and bounce-buffer paths, disconnect during active commands, LUN link/unlink port counts, target-core status/data callbacks, and module unload cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_tcm.c -->
