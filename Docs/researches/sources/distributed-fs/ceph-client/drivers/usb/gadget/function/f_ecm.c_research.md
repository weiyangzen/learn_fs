# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_ecm.c

## Purpose
`f_ecm.c` implements the USB CDC Ethernet Control Model function. It exposes a USB Ethernet network interface using a CDC control interface, a data interface with alternate settings, bulk data endpoints via `u_ether`, and an interrupt notification endpoint for network connection and speed changes. The configfs function name is `ecm`.

## Important APIs, Types, and Functions
`struct f_ecm` embeds `struct gether`, stores control/data interface IDs, CDC MAC string, notify endpoint/request, notification state/count, and open state. Descriptors include IAD, CDC header/union/ethernet descriptors, data altsetting 0 with no endpoints, data altsetting 1 with bulk endpoints, and FS/HS/SS notification descriptors. Important functions are `ecm_setup()`, `ecm_set_alt()`, `ecm_get_alt()`, `ecm_disable()`, `ecm_do_notify()`, `ecm_notify()`, `ecm_notify_complete()`, `ecm_open()`, `ecm_close()`, `ecm_bind()`, `ecm_unbind()`, `ecm_suspend()`, `ecm_resume()`, `ecm_get_status()`, `ecm_alloc_inst()`, and `ecm_alloc()`.

## Control Flow
Instance allocation creates `f_ecm_opts`, initializes a default Ethernet netdev with `gether_setup_default()`, and exposes dev/host address, qmult, and ifname attributes. Function allocation increments the option refcount, captures the host MAC in CDC string format, and sets callback pointers. Bind validates `can_support_ecm()`, registers or attaches the shared netdev to the gadget, attaches strings, assigns two interfaces, autoconfigures IN/OUT/notify endpoints, allocates a notify request buffer, mirrors endpoint addresses into HS/SS descriptors, assigns descriptors, and sets `port.open/close` callbacks. Runtime activation is through `SET_INTERFACE`: control alt 0 enables notify; data alt 1 configures data endpoints, sets ZLP/filter defaults, and calls `gether_connect()`. Alt 0 disconnects data traffic. Host packet filter control requests update `port.cdc_filter`.

## State and Persistence
The network device is owned by `f_ecm_opts` and may be shared across bound function instances through `bind_count`, `bound`, and `refcnt` conventions from `u_ether_configfs`. `notify_state` sequences CONNECT then SPEED notifications; `notify_count` prevents multiple in-flight notify requests. `is_open` reflects netdev open/close callbacks. `get_alt()` reports data interface alt 1 when the IN endpoint is enabled. State resets on disable/unbind, where notify requests are dequeued/freed and the gadget is detached from the netdev when no longer bound.

## Dependencies and Integration Points
ECM depends on `u_ether` for netdev setup, gadget attach/detach, connect/disconnect, bitrate, suspend/resume, and data transfer. Configfs attributes come from `u_ether_configfs.h`; ECM-specific shared declarations are in `u_ecm.h`. Composite integration uses string/interface ID allocation, endpoint autoconfig, speed-specific endpoint configuration, descriptor assignment, USB 3 function wake status, and function registration.

## Risks
The comments call out weak locking around `is_open` and packet filter updates. Notification sequencing allows connect notifications to overlap conceptually, guaranteeing speed notification but not strict ECM text ordering. Bind has several allocation/registration stages and relies on cleanup attributes (`__free`) plus unbind detach logic. Hosts that do not poll the notification endpoint can leave notifications in FIFO. ECM requires alternate settings and a valid `get_alt()`; errors in alt handling can expose endpoints at the wrong time.

## Test Signals
Run ECM on hosts with CDC ECM support at FS/HS/SS, verify interface alt 0/1 transitions, packet filter class request behavior, netdev open/close notification pairs, speed-change notifications, unplug/rmmod/SET_CONFIGURATION/SET_INTERFACE while open and closed, suspend/resume, function remote wake status bits, and configfs address/qmult/ifname attributes.
