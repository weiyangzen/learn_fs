# sources/distributed-fs/ceph-client/net/ethtool/module_fw.h

## Purpose
This header defines the shared data structures and function declarations for ethtool module firmware flashing, especially CMIS firmware update work and notifications.

## Important APIs, Types, And Functions
`struct ethnl_module_fw_flash_ntf_params` stores netlink port id, sequence, and `closed_sock`. `struct ethtool_module_fw_flash_params` stores an optional big-endian module password. `struct ethtool_cmis_fw_update_params` bundles the target netdevice, flash params, notification params, and firmware image. `struct ethtool_module_fw_flash` is the async work/list/refcount wrapper used by `module.c`. The header declares socket-destroy, notification, and `ethtool_cmis_fw_update()` entry points.

## Control Flow
`module.c` allocates `struct ethtool_module_fw_flash`, fills the nested CMIS update params, queues `work`, and later the worker calls `ethtool_cmis_fw_update()`. CMIS code calls the declared notification helpers to emit started, progress, error, and completed messages.

## State And Persistence
The structures hold transient in-kernel state for one flash operation. They persist only until the worker releases firmware, drops the netdev hold, and frees the wrapper.

## Dependencies And Integration Points
The header depends on UAPI ethtool definitions, netlink internal socket types, `struct net_device`, `struct firmware`, workqueues, and netdevice reference tracking. It forms the contract between `module.c` and CMIS firmware update code.

## Risks And Edge Cases
The notification sequence is mutable and shared with the worker. `closed_sock` is advisory and suppresses notifications only after socket destruction is observed. Password validity is bitfield state, so initialization must zero the struct before optional password assignment.

## Test Signals
Header-level validation is compile-time: consumers must agree on struct layout and declarations. Runtime tests should verify that CMIS update code can call all notification helpers and that socket-private teardown correctly toggles `closed_sock`.
