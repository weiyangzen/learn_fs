# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_table.c

## Purpose
This file implements direct-rule flow table lifecycle and miss-action wiring. It creates software-owned hardware flow tables rooted at STE hash-table anchors, initializes RX/TX/FDB table state, and exposes table IDs back to the flow steering layer.

## Important APIs, Types, And Functions
Public functions are `mlx5dr_table_create()`, `mlx5dr_table_destroy()`, `mlx5dr_table_set_miss_action()`, `mlx5dr_table_get_id()`, and `mlx5dr_table_get_from_fs_ft()`. Internal helpers initialize/uninitialize NIC RX/TX anchors, FDB pairs, create/destroy the firmware flow table, and update miss paths.

## Control Flow
Table creation increments the domain refcount, allocates `struct mlx5dr_table`, initializes per-domain-type anchors under the domain lock, creates a firmware flow table with `sw_owner = true`, records debug state, and returns the table. RX/TX tables get one anchor; FDB tables get both RX and TX anchors. Creation passes the anchor ICM addresses to firmware as roots.

Miss-action setting validates that only destination-table actions are accepted, locks the domain, updates RX and/or TX miss chains depending on domain type, swaps the table's stored miss action, and adjusts action refcounts. The NIC miss update finds the last matcher anchor if matchers exist, otherwise the table start anchor, then posts a miss connection with `mlx5dr_ste_htbl_init_and_postsend()`.

Table destruction refuses to run with outstanding table references, removes debug state, destroys the firmware table, releases anchors, drops any miss action reference, decrements the domain refcount, and frees memory.

## State And Persistence
State is held in `struct mlx5dr_table`: level, flags, table type/id, RX/TX anchors, matcher lists, miss action, refcount, and debug node. Hardware-visible persistence is the firmware flow table and ICM-rooted STE anchors. Refcounts protect domain, table, hash-table, and action lifetimes.

## Dependencies And Integration Points
The file depends on `dr_types.h` for all structures and internal APIs. It calls ICM hash-table allocation/free, STE postsend initialization, firmware flow-table create/destroy commands, and debug table registration. `fs_dr.c` uses these APIs as the flow steering backend.

## Risks
Miss-action updates partially program RX then TX for FDB; a failure after one side may leave hardware state changed before returning an error. Refcount checks protect against destroying active tables but rely on all action/rule users to hold references correctly. Anchor initialization and firmware table creation must unwind in the right order to avoid leaked ICM chunks.

## Test Signals
Tests should create/destroy NIC RX, NIC TX, and FDB tables, set and clear miss actions, chain tables through miss actions, and verify refcount busy failures. Error-injection tests around anchor postsend and firmware create/destroy paths would exercise unwinds.
