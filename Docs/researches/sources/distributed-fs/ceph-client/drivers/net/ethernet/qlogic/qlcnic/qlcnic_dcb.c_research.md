# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_dcb.c

## Purpose
This file implements Data Center Bridging (DCB/DCBX) support for qlcnic adapters when `CONFIG_QLCNIC_DCB` is enabled. It registers adapter-local DCB state, selects 82xx or 83xx DCB operations, queries firmware DCB capabilities and CEE parameters, maps firmware mailbox bitfields into kernel DCBNL-visible structures, refreshes state on asynchronous events, and exposes read-only/LLD-managed DCB operations to the networking stack.

## Important APIs, Types, And Functions
- DCB operation tables: `qlcnic_82xx_dcb_ops` and `qlcnic_83xx_dcb_ops` implement the function-pointer interface declared in `qlcnic_dcb.h`.
- Registration/lifecycle: `qlcnic_register_dcb()`, `__qlcnic_dcb_attach()`, `__qlcnic_dcb_free()`, `__qlcnic_init_dcbnl_ops()`, and `__qlcnic_dcb_get_info()`.
- Firmware query paths: `__qlcnic_dcb_query_hw_capability()`, `__qlcnic_dcb_get_capability()`, `qlcnic_82xx_dcb_get_hw_capability()`, `qlcnic_83xx_dcb_get_hw_capability()`, `qlcnic_82xx_dcb_query_cee_param()`, `qlcnic_83xx_dcb_query_cee_param()`, and corresponding `get_cee_cfg()` functions.
- Mapping helpers: `qlcnic_dcb_fill_cee_tc_params()`, `qlcnic_dcb_fill_cee_pg_params()`, `qlcnic_dcb_fill_cee_app_params()`, `qlcnic_dcb_map_cee_params()`, and `qlcnic_dcb_data_cee_param_map()`.
- AEN refresh: `qlcnic_dcb_aen_work()`, `qlcnic_82xx_dcb_aen_handler()`, and `qlcnic_83xx_dcb_aen_handler()`.
- DCBNL operations: `qlcnic_dcb_get_state()`, `getpgtccfgtx`, `getpgbwgcfgtx`, `getpfccfg`, `getcap`, `getnumtcs`, `getapp`, `getpfcstate`, `getdcbx`, `getfeatcfg`, peer app table/info, and CEE peer PG/PFC getters.

## Control Flow
`qlcnic_register_dcb()` skips SR-IOV VFs, allocates `struct qlcnic_dcb`, attaches it to the adapter, and assigns ops based on adapter generation. During 83xx initialization, `qlcnic_dcb_enable()` calls `__qlcnic_dcb_attach()` to initialize delayed work, create a single-thread workqueue, and allocate config/parameter buffers. `qlcnic_dcb_get_info()` first queries capabilities; if firmware reports DCBX plus TSA/ETS support, `QLCNIC_DCB_STATE` is set. It then queries local, operational, and peer CEE parameters and maps them into `dcb->cfg`.

82xx parameter queries use a DMA response buffer containing little-endian `struct qlcnic_82xx_dcb_param_mbx_le`; 83xx queries use mailbox response arguments directly with a firmware-version bit in the command. Mapping fills TC, priority group, PFC, and application priority state. Operational app entries are registered with `dcb_setapp()`, and `dcbnl_cee_notify()` notifies userspace. AEN handlers set a mode bit, optionally update DCB enabled state for 83xx based on event data, queue work, and the worker refreshes CEE config before clearing the mode bit.

## State And Persistence Behavior
Persistent state is held in `adapter->dcb`, `dcb->state`, `dcb->cfg`, and `dcb->param`. `QLCNIC_DCB_STATE` means DCB is usable and controls whether `netdev->dcbnl_ops` is installed. `QLCNIC_DCB_AEN_MODE` serializes asynchronous refresh handling and is waited on during free. The firmware CEE data is cached in both raw mailbox form (`struct qlcnic_dcb_mbx_params`) and mapped kernel-facing form (`struct qlcnic_dcb_cfg`). Application priorities may also be persisted in the kernel DCB app table via `dcb_setapp()`.

## Dependencies And Integration Points
The file depends on qlcnic mailbox command allocation/issue, adapter generation detection, netdev DCBNL APIs, workqueues, delayed work, firmware DCB command IDs, CEE structures, and device AEN delivery. `qlcnic_dcb.h` provides no-op wrappers when the config option is disabled, so callers in init/reset code can remain unconditional.

## Risks And Edge Cases
- DCB is LLD-managed and mostly read-only; attempts to infer writable behavior from DCBNL ops would be incorrect.
- The 83xx mailbox response parsing uses fixed response indices and copies a fixed 16-DWORD block for each parameter type; command metadata and firmware ABI must match exactly.
- `qlcnic_dcb_prio_count()` returns the first set priority bit, not a population count, so app priority mapping assumes one priority bit is meaningful.
- Free waits while `QLCNIC_DCB_AEN_MODE` is set; if queued work never runs or hangs, teardown can wait repeatedly.
- `qlcnic_dcb_cee_peer_get_pg()` indexes `peer->tc_cfg[i]` while iterating PG IDs; unusual PG/TC mappings could produce incomplete peer PG reporting.
- DCBNL ops access `adapter->dcb` and nested config without broad locking beyond AEN mode, so reset/free ordering is important.

## Test Signals
Useful signals include DCB registration skipped for SR-IOV VFs, workqueue/config allocation failures, firmware DCB capability errors, `QLCNIC_DCB_STATE` set/cleared behavior, DCBNL output for PG/PFC/app/peer data, `dcbnl_cee_notify()` after AEN refresh, and teardown under active AEN refresh without use-after-free or stuck waits.
