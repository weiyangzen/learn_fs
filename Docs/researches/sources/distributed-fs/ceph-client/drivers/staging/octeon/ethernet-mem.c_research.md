# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mem.c

## Purpose
Fills and drains Octeon FPA hardware memory pools used for packet buffers, work queue entries, and output buffers.

## Important APIs, Types, And Functions
Exports `cvm_oct_mem_fill_fpa()` and `cvm_oct_mem_empty_fpa()`. Internal helpers are `cvm_oct_fill_hw_skbuff()`, `cvm_oct_free_hw_skbuff()`, `cvm_oct_fill_hw_memory()`, and `cvm_oct_free_hw_memory()`.

## Control Flow
Packet-pool fills allocate skbs, reserve to a 128-byte boundary with extra headroom, save the skb pointer just before data, and free the aligned data pointer to FPA. Non-packet pools allocate raw kmalloc memory with alignment padding and save the original pointer before the aligned block. Emptying reverses the process by allocating from FPA until empty, recovering the original skb or kmalloc pointer, and freeing it.

## State And Persistence
State lives in FPA pools and hidden back-pointers stored immediately before aligned buffers. No durable state exists.

## Dependencies And Integration Points
Depends on CVMX FPA allocation/free primitives, skb allocation/free, kmalloc/kfree, and pool constants from Octeon headers.

## Risks
Correctness relies on alignment math and metadata stored before the buffer. Drain warnings detect count mismatches but cannot repair leaks. Packet pool buffers are skbs, while other pools are raw memory; using the wrong pool id would free incorrectly.

## Test Signals
Fill and empty each pool, simulate partial allocation failure, verify 128-byte alignment, validate skb back-pointer recovery, check warning paths for too many/missing buffers, and run RX/TX stress with FPA refill.
