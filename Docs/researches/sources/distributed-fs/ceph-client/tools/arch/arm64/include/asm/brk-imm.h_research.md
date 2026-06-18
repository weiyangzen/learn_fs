# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/brk-imm.h

## Purpose
Defines arm64 BRK immediate values used to identify software breakpoint/trap purposes.

## Important APIs, Types, And Functions
- Defines immediates for kprobes, uprobes, kprobe single-step, kretprobes, intentional fault, KGDB dynamic/compiled breakpoints, BUG/WARN traps, KASAN, UBSAN, and CFI traps.
- `CFI_BRK_IMM_TARGET`, `CFI_BRK_IMM_TYPE`, `CFI_BRK_IMM_BASE`, and `CFI_BRK_IMM_MASK` define CFI immediate bit fields.

## Control Flow
No runtime flow; constants are used by code that emits or decodes `BRK #imm16` instructions.

## State And Persistence
No state. Constants are ABI/debugging conventions between kernel and tools.

## Dependencies And Integration Points
Used by arm64 tooling and possibly disassembly/diagnostic paths that need to classify break instructions.

## Risks
Incorrect immediates can misclassify traps or conflict with reserved ranges, degrading debugging, sanitizers, probes, or CFI diagnostics.

## Test Signals
Compare against kernel arm64 `brk-imm.h`, run probe/BUG/KASAN/UBSAN/CFI decoding tests, and verify tools classify `BRK` immediates correctly.
