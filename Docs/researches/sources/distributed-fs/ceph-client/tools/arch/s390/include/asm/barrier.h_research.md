# sources/distributed-fs/ceph-client/tools/arch/s390/include/asm/barrier.h

## Purpose
s390 tools memory-barrier header.

## Important APIs, Types, and Functions
Defines `__ASM_BARRIER` as `bcr 14,0` with z196 features or `bcr 15,0` otherwise, maps `mb()/rmb()/wmb()` to that instruction, and provides release/acquire helpers.

## Control Flow, State, and Persistence
No persistent state. Barrier macros impose ordering at expansion sites.

## Dependencies and Integration Points
Used by tools code requiring Linux barrier primitives on s390.

## Risks and Test Signals
Risks include Kconfig feature mismatch and assuming compiler-only release/acquire is sufficient for all contexts. Test signals are s390 tools builds and concurrency primitive tests.
