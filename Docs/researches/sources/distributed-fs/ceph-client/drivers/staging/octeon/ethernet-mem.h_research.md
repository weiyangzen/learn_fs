# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mem.h

## Purpose
Declaration header for Octeon FPA pool fill/drain helpers.

## Important APIs, Types, And Functions
Declares `cvm_oct_mem_fill_fpa(int pool, int size, int elements)` and `cvm_oct_mem_empty_fpa(int pool, int size, int elements)`.

## Control Flow
Core and RX code call these helpers to populate and replenish hardware pools and to empty them during module removal.

## State And Persistence
No state; prototypes only.

## Dependencies And Integration Points
Included by `ethernet.c`, `ethernet-rx.h`, and `ethernet-mem.c`.

## Risks
Callers must pass the correct pool id, element size, and expected count because the implementation uses those to choose skb versus raw-memory handling.

## Test Signals
Build all call sites and verify pool fill/empty behavior through the implementation tests described for `ethernet-mem.c`.
