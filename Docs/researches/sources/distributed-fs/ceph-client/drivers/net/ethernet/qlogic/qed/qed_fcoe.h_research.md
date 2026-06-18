# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_fcoe.h

## Purpose
`qed_fcoe.h` declares the internal FCoE support hooks used by the `qed` core resource lifecycle and statistics paths. It also provides compile-time stubs when `CONFIG_QED_FCOE` is disabled, allowing the rest of the core driver to compile while treating FCoE allocation as unsupported.

## Important APIs, Types, And Functions
`struct qed_fcoe_info` holds a spinlock protecting connection resources and a `free_list` of reusable `struct qed_fcoe_conn` objects owned by the implementation. When FCoE is enabled, the header declares `qed_fcoe_alloc()`, `qed_fcoe_setup()`, `qed_fcoe_free()`, and `qed_get_protocol_stats_fcoe()`. When FCoE is disabled, `qed_fcoe_alloc()` returns `-EINVAL`, setup/free are no-ops, and protocol stats collection is a no-op.

## Control Flow
The core device flow calls these hooks from `qed_resc_alloc()`, `qed_resc_setup()`, `qed_resc_free()`, and MCP/statistics paths only when the hwfn personality is FCoE or when protocol stats are requested. The enabled implementation allocates per-hwfn state first, initializes task contexts during setup, frees cached connection resources during teardown, and reads protocol stats on demand. The disabled implementation short-circuits those flows.

## State And Persistence Behavior
The header defines the visible state container for FCoE connection-resource management. Actual persistent state lives in `p_hwfn->p_fcoe_info`, the connection free list, and firmware contexts managed by `qed_fcoe.c`. The disabled stubs do not allocate or mutate state.

## Dependencies And Integration Points
The header includes kernel list/slab/spinlock types, `linux/qed/qed_fcoe_if.h`, `qed_chain.h`, and internal core headers for `qed`, HSI, MCP, and slowpath structures. It is included by `qed_dev.c` and `qed_fcoe.c`, binding the generic device lifecycle to optional FCoE support.

## Risks And Edge Cases
Callers must not assume FCoE support is present; the disabled stub returns `-EINVAL` from allocation. Because `qed_fcoe_info.lock` protects connection resources, implementation paths that manipulate the free list must initialize the lock before use and avoid mixing unlocked hash-table state with locked free-list state. The stats stub silently leaves caller-provided stats unchanged, so callers should account for configuration.

## Test Signals
Compile tests should cover both enabled and disabled FCoE configurations. Enabled runtime signals include successful allocation/setup/free in the FCoE personality and non-empty statistics after traffic. Disabled tests should verify the core handles `qed_fcoe_alloc()` returning `-EINVAL` only when an FCoE personality is incorrectly requested without support and that non-FCoE builds do not reference missing implementation symbols.
