# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/t3cdev.h

## Purpose

`t3cdev.h` defines the Chelsio T3 offload-device interface object shared by the low-level `cxgb3` adapter driver and upper-layer offload clients. It gives clients a compact `struct t3cdev` with identity, list membership, associated Linux netdev/proc entry, packet send/receive/control callbacks, neighbor update hook, and opaque per-layer extension pointers.

## Important APIs and Types

- `T3CNAMSIZ` fixes the device-name buffer length at 16 bytes.
- `enum t3ctype` identifies chip generation/revision families as `T3A`, `T3B`, or `T3C`.
- `struct t3cdev` is the central contract. Important fields are `name`, `type`, `ofld_dev_list`, `lldev`, `proc_dir`, `send`, `recv`, `ctl`, `neigh_update`, `priv`, `l2opt`, `l3opt`, `l4opt`, `ulp`, and `ulp_iscsi`.

## Control Flow and Usage

The header has no executable control flow. At runtime, the adapter embeds or owns a `struct t3cdev` and fills its function pointers. `sge.c` calls `adapter->tdev.recv()` when delivering offload receive bundles and exposes `t3_offload_tx()` as the lower-level send path. Offload clients use `send()` to submit CPL/work-request skbs, `recv()` to receive arrays of skbs, `ctl()` for control operations, and `neigh_update()` to react to neighbor-table changes.

## State and Persistence Behavior

The structure holds runtime-only kernel state. `ofld_dev_list` links devices into an offload registry; `lldev` ties offload traffic to the low-level netdev; `proc_dir` exposes per-device procfs state; `priv` and the layer option pointers hold driver/client-owned data. `l2opt` is RCU-protected, so readers and writers must use the appropriate RCU discipline. No fields are persistent across module unload or reboot.

## Dependencies and Integration Points

The header depends on kernel list, atomic, netdevice, procfs, skbuff, and neighbor declarations. It integrates with `adapter.h` through the embedded adapter offload device, with `cxgb3_offload.c/.h` for registration and client dispatch, with `sge.c` for packet movement, and with L2/L3/L4/ULP offload modules that store private state in the opaque pointers.

## Risks and Edge Cases

- Callback pointer validity and lifetime are critical; `send`, `recv`, and `ctl` can be invoked from networking or NAPI contexts and must obey context constraints.
- `recv()` receives an array of skb pointers and count; ownership transfer must be clear to avoid skb leaks or double frees.
- `l2opt` is annotated `__rcu`; direct dereference outside RCU-safe paths is unsafe.
- The interface is minimal and relies on external conventions for request IDs, priority bits, queue selection, and skb layout.

## Test Signals

Useful signals include offload client registration/unregistration, successful `send()` to SGE queues, batched `recv()` delivery under NAPI and interrupt modes, neighbor-update propagation, proc entry lifecycle, and RCU/lifetime checks under module unload or adapter reset.
