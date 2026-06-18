<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_64.h

## Purpose
This header defines SPARC64 hard IRQ accounting and stack integration.

## Important APIs, Types, and Functions
It provides SPARC64-specific hardirq declarations used by generic IRQ handling and per-CPU accounting.

## Control Flow
SPARC64 interrupt entry/exit code updates hardirq state and may switch stacks according to architecture support.

## State and Persistence Behavior
Interrupt accounting is per-CPU runtime state managed elsewhere.

## Dependencies and Integration Points
It integrates with generic IRQ, lockdep, softirq-on-own-stack support, and SPARC64 trap entry.

## Risks
Incorrect IRQ accounting affects lockdep and can hide interrupt nesting bugs.

## Test Signals
Run interrupt-heavy workloads with lockdep/trace irqflags and validate no hardirq/preempt imbalance warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_64.h -->
