# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/smt.h

## Purpose
Declares the Chelsio Source MAC Table state model and public SMT APIs used by filter and firmware-event code.

## Important APIs, Types, and Functions
Defines SMT states `SMT_STATE_SWITCHING`, `SMT_STATE_UNUSED`, and `SMT_STATE_ERROR`, fixed `SMT_SIZE` of 256, `struct smt_entry`, and `struct smt_data`. Declares `t4_init_smt`, `cxgb4_smt_alloc_switching`, `cxgb4_smt_release`, and `do_smt_write_rpl`.

## Control Flow
The header has no runtime control flow. Its declarations establish the locking/state contract: the table has a global rwlock and each entry has its own spinlock protecting state, source MAC, and refcount updates.

## State and Persistence Behavior
`struct smt_entry` persists a hardware table index, source MAC, PF/VF selector, state, refcount, and lock. `struct smt_data` persists the table size and flexible array. Hardware persistence is handled by the implementation's CPL write path.

## Dependencies and Integration Points
Includes Linux spinlock, Ethernet address, and atomic headers and forward-declares `struct adapter` and `struct cpl_smt_write_rpl`. Included by `smt.c`, filter code, and main firmware reply dispatch.

## Risks
The fixed table size and state enum are hardware ABI assumptions. Refcount is a plain `int` protected by locks; users must obey the locking contract. Any layout changes affect allocation and teardown paths that use `kvzalloc_flex`/`kvfree`.

## Test Signals
Compile coverage with filter code enabled, add/delete filter tests that call allocation and release, and firmware reply dispatch tests for `CPL_SMT_WRITE_RPL` all validate this interface.
