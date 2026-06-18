# sources/distributed-fs/ceph-client/drivers/soc/qcom/smem_state.c

## Purpose

`smem_state.c` provides a small registry for named Qualcomm SMEM-backed state providers. Clients look up state handles from DT phandles and update bit masks through provider callbacks. SMP2P registers outbound entries through this API.

## Important APIs, Types, and Functions

Exported APIs are `qcom_smem_state_update_bits()`, `qcom_smem_state_get()`, `qcom_smem_state_put()`, `devm_qcom_smem_state_get()`, `qcom_smem_state_register()`, and `qcom_smem_state_unregister()`. `struct qcom_smem_state` stores kref, orphan flag, registry list node, OF node, provider private pointer, and ops.

## Control Flow

Providers call `qcom_smem_state_register()` with an OF node, ops, and private data; the state is inserted into a global list. Clients call `qcom_smem_state_get()`, optionally resolving a named index, parse `qcom,smem-states` with one bit argument, and search the registry by OF node. `update_bits()` rejects orphaned states and dispatches to provider ops. `put()` decrements the kref under the list mutex; unregister marks the state orphaned and drops the provider reference.

## State and Persistence Behavior

Registry state is in-memory only. The state value itself lives in the provider, commonly an SMP2P SMEM word. Handles can outlive provider unregister only until their kref is put; `orphan` prevents further updates.

## Dependencies and Integration Points

It depends on OF phandle parsing, device resources, lists, mutexes, krefs, and `<linux/soc/qcom/smem_state.h>`. SMP2P is the primary provider in this subset, while remoteproc/subsystem clients are typical consumers.

## Risks and Edge Cases

`qcom_smem_state_unregister()` sets `orphan` without holding `list_lock`, while `qcom_smem_state_update_bits()` reads it locklessly. `qcom_smem_state_update_bits()` does not take a reference, so callers must hold a valid handle. A missing provider returns `-EPROBE_DEFER`, which can defer clients indefinitely if DT references are wrong. The devm wrapper allocates devres before lookup and frees it on failure.

## Test Signals

Test provider/client probe ordering, named and unnamed lookups, invalid cell counts, missing names, unregister while clients hold references, update after orphan returns `-ENXIO`, missing update op returns `-ENOTSUPP`, and devm cleanup on client removal.
