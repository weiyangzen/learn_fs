# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq.h

## Purpose
`xe_memirq.h` declares the memory-based interrupt public API used by IRQ, LRC, GuC, and HWE code.

## Important APIs, Types, And Functions
- Declares init, source/status/enable pointer getters, reset/postinstall, HWE and global handlers, GuC setup, and SW_INT_0 pending query.

## Control Flow
Initialization allocates memory IRQ pages before LRC or GuC programming. LRC code queries GGTT pointers, IRQ code toggles/dispatches handlers, and recovery code can query SW_INT_0 pending state.

## State And Persistence
The header owns no state; it operates on `struct xe_memirq` defined in the types header.

## Dependencies And Integration Points
Forward-declares GuC, hardware engine, and memirq structures. It is the contract between memory IRQ implementation and the rest of Xe interrupt/context setup.

## Risks
Callers must only use pointer getters after successful `xe_memirq_init()` and when the device actually uses memory IRQs. Dispatch helpers assume the BO and maps are valid.

## Test Signals
Build/link tests and runtime assertions around pointer use before/after init, reset, and teardown.
