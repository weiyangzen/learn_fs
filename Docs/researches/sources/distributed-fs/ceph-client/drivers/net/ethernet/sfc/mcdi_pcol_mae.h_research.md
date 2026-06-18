# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol_mae.h

Purpose: this small protocol-extension header supplies one MCDI Match-Action Engine constant that is missing from the main generated `mcdi_pcol.h`. It exists so MAE action-set allocation code can pass a guaranteed-null counter-list identifier even before the corresponding firmware API is released in the shared protocol header.

Important API: `MC_CMD_MAE_COUNTER_LIST_ALLOC_OUT_COUNTER_LIST_ID_NULL` is defined as `0xffffffff`. There are no functions or persistent state; the header only exposes the sentinel value under an include guard.

Control flow and integration: consumers include this header alongside `mcdi_pcol.h` when building MAE commands, especially commands that need to express "no counter list" for action-set allocation. The dependency is intentionally one-way from driver MAE code to this compatibility definition.

Risks: the value must remain aligned with firmware semantics. If a later official `mcdi_pcol.h` defines the same name differently or starts providing a duplicate definition, build or behavior conflicts are possible. Test signals are compile coverage of MAE users and runtime TC/MAE offload tests that allocate action sets with and without counters.
