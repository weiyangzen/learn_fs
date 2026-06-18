# sources/distributed-fs/ceph-client/arch/csky/kernel/atomic.S

## Purpose

provides the C-SKY cmpxchg trap helper used where atomic compare/exchange must be performed from a
controlled exception context

## Important APIs, Types, and Functions

Source read size: 61 lines, 894 bytes. Includes: `linux/linkage.h`, `abi/entry.h`. Assembly/global
entries: `csky_cmpxchg`, `csky_cmpxchg_ldw`, `csky_cmpxchg_stw`.

## Control Flow and Behavior

csky_cmpxchg saves EPC/EPSR/USP, performs ldex/stex when available or exposes ldw/stw patch labels
for fallback handling, restores state, and returns through rte

## State and Persistence

state changes are limited to the memory word being conditionally exchanged and restored control
registers

## Dependencies and Integration Points

depends on ABI entry macros, CPU_HAS_LDSTEX, trap sizing, exception return semantics, and
atomic/cmpxchg callers

## Risks and Test Signals

exclusive-store retry logic and fallback labels must be exact; atomic API tests and SMP stress are
the main signals
