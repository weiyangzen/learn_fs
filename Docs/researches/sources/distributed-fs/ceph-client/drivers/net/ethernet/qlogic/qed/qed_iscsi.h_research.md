# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iscsi.h

## Purpose
`qed_iscsi.h` declares internal iSCSI support state and lifecycle/statistics entry points, with compile-time stubs when `CONFIG_QED_ISCSI` is disabled.

## Important APIs, Types, and Functions
- `struct qed_iscsi_info` stores the connection-resource spinlock, reusable connection free list, max outstanding task count, async event context, and event callback.
- Enabled builds declare `qed_iscsi_alloc()`, `qed_iscsi_setup()`, `qed_iscsi_free()`, and `qed_get_protocol_stats_iscsi()`.
- Disabled builds provide stubs that return `-EINVAL` for allocation and no-op setup/free/stats functions.

## Control Flow
The core driver allocates iSCSI info during feature setup, initializes its lock during setup, frees cached connections during teardown, and asks for protocol stats when management firmware or reporting paths need storage counters. Public iSCSI operations are exported from `qed_iscsi.c`, while this header covers internal core-driver integration.

## State and Persistence
The header defines `p_hwfn->p_iscsi_info` contents: free-list state, locking, event callback state, and task limits. State is memory-resident only.

## Dependencies and Integration Points
It includes Linux list/spinlock/slab types, QED TCP/iSCSI public interfaces, QED chains, core QED state, HSI, MCP, and SPQ headers. It is consumed by core QED setup/teardown and `qed_iscsi.c`.

## Risks
- Callers must handle `-EINVAL` when iSCSI support is not built.
- The spinlock is not initialized by allocation alone; setup sequencing matters.
- `max_num_outstanding_tasks` is declared here but not managed in this header, so implementation/users must keep it consistent with PF params and firmware limits.

## Test Signals
Build both with and without `CONFIG_QED_ISCSI`. Runtime signals include successful allocation/setup/free sequencing, no stale free-list entries after teardown, and valid protocol stats when enabled.
