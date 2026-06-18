# sources/distributed-fs/ceph-client/include/linux/rpmsg.h

## Purpose
`rpmsg.h` is the main Remote Processor Messaging bus API. It lets drivers bind to rpmsg channels, create endpoints, send messages, receive callbacks, poll endpoints, and apply transport flow control.

## Important APIs, types, and functions
Core types include `struct rpmsg_channel_info`, `struct rpmsg_device`, `struct rpmsg_endpoint`, `struct rpmsg_driver`, `rpmsg_rx_cb_t`, and `rpmsg_flowcontrol_cb_t`. Important helpers are `rpmsg16_to_cpu()`, `cpu_to_rpmsg16()`, `rpmsg32_to_cpu()`, `cpu_to_rpmsg32()`, `rpmsg64_to_cpu()`, and `cpu_to_rpmsg64()`. Enabled APIs include `rpmsg_register_device_override()`, `rpmsg_register_device()`, `rpmsg_unregister_device()`, `__register_rpmsg_driver()`, `unregister_rpmsg_driver()`, `rpmsg_create_ept()`, `rpmsg_destroy_ept()`, `rpmsg_send()`, `rpmsg_sendto()`, `rpmsg_trysend()`, `rpmsg_trysendto()`, `rpmsg_poll()`, `rpmsg_get_mtu()`, and `rpmsg_set_flow_control()`.

## Control flow, state, and persistence
Transports instantiate `rpmsg_device` objects with source/destination addresses and endian mode. Drivers register an `rpmsg_driver`; bus matching invokes `probe`, binds the channel endpoint, and calls the driver's receive callback for inbound messages matching the endpoint address. Explicit endpoints carry a callback, private pointer, reference count, callback mutex, local address, and endpoint ops. Disabled builds warn and return `-ENXIO`/`NULL`. State persists as device model objects and endpoint references while the remote processor/channel is alive.

## Dependencies and integration points
The header integrates with device core, module device tables, krefs, mutexes, poll, UAPI rpmsg definitions, byteorder wrappers, remoteproc/virtio transports, userspace rpmsg character devices, and vendor transports such as Qualcomm GLINK/SMD and MediaTek rpmsg.

## Risks and test signals
Risks include endpoint use-after-destroy, callback changes without holding `cb_lock`, MTU overrun, blocking send in atomic context, endian mismatches, stale driver overrides, and flow-control deadlocks. Test signals include driver registration/matching, endpoint create/destroy refcounting, inbound callback dispatch, send/trysend behavior under full vrings, poll readiness, MTU bounds, flow-control pause/resume, and disabled-config stub coverage.
