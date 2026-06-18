# sources/distributed-fs/ceph-client/net/atm/pvc.c

## Purpose
`pvc.c` implements the `PF_ATMPVC` socket family for permanent virtual circuits. It wraps common VCC operations with PVC-specific address validation and socket operation registration.

## Important APIs and Functions
- `pvc_bind` / `pvc_connect`: validate `sockaddr_atmpvc`, require QoS via `ATM_VF_HASQOS`, apply partial VPI/VCI state, and call `vcc_connect`.
- `pvc_getname`: returns the bound interface/VPI/VCI when the VCC has a device and address.
- `pvc_setsockopt` / `pvc_getsockopt`: lock the socket and delegate to common VCC options.
- `pvc_proto_ops`: socket operations table delegating release, poll, ioctl, sendmsg, and recvmsg to common functions.
- `atmpvc_init` / `atmpvc_exit`: register/unregister the protocol family.

## Control Flow
Socket creation is limited to `init_net`, assigns `pvc_proto_ops`, and calls `vcc_create` with `PF_ATMPVC`. Binding and connecting share the same path. Once QoS is configured, `vcc_connect` attaches the VCC to a device/VPI/VCI and subsequent send/receive use the common VCC data path.

## State and Persistence
PVC-specific state is stored in the underlying `atm_vcc`: selected device, VPI/VCI, QoS flags, address flag, and common socket queues. The file itself persists only the static `proto_ops` and `net_proto_family`.

## Dependencies and Integration
Depends on `common.h` for shared VCC behavior and `resources.h` for device/VCC resource context. It uses Linux socket family registration and rejects non-init network namespaces.

## Risks and Test Signals
Risks include incorrect acceptance of partial/unspecified VPI/VCI, missing socket lock coverage around shared VCC mutations, and namespace behavior. Test signals include creating `AF_ATMPVC` sockets, setting QoS before bind, bind/connect failure without QoS, `getsockname` after connect, compat/native ioctls through the PVC ops, and family unregister during module/core teardown.
