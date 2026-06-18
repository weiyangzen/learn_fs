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
