<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_work.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_work.h

## Purpose
Architecture hook telling generic irq_work whether x86 can deliver irq_work through an interrupt vector. The header is 19 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/cpufeature.h>`

Notable constants/macros: `#define _ASM_IRQ_WORK_H`

Notable declarations and inline helpers: `#define _ASM_IRQ_WORK_H`; `static inline bool arch_irq_work_has_interrupt(void)`

## Control Flow
The helper returns true when local APIC/IRQ_WORK_VECTOR support is available, otherwise false for fallback behavior.

## State and Persistence
State is absent; behavior is based on build/CPU feature configuration.

## Dependencies and Integration Points
Depends on cpufeature/local APIC configuration and generic irq_work core.

## Risks
Risks are missed wakeups or slower fallback if capability is misreported.

## Test Signals
Tests should run irq_work selftests on APIC and non-APIC configs, including CPU hotplug and nohz contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_work.h -->
