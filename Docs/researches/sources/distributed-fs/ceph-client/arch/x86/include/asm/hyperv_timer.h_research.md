<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hyperv_timer.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hyperv_timer.h

## Purpose
Hyper-V synthetic timer declarations for x86 guest clockevent integration. The header is 9 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/msr.h>`

Notable constants/macros: `#define _ASM_X86_HYPERV_TIMER_H`; `#define hv_get_raw_timer() rdtsc_ordered()`

Notable declarations and inline helpers: `#define _ASM_X86_HYPERV_TIMER_H`; `#define hv_get_raw_timer() rdtsc_ordered()`

## Control Flow
The implementation registers per-CPU synthetic timer devices and receives Hyper-V timer callbacks through architecture vector plumbing.

## State and Persistence
State lives in Hyper-V synthetic timer MSRs/messages and clockevent device data managed outside this header.

## Dependencies and Integration Points
Depends on CONFIG_HYPERV, Hyper-V vector definitions, clockevents, and hypervisor callback setup.

## Risks
Risks include missing callback vector routing, CPU hotplug timer state loss, and guest clock drift under reenlightenment.

## Test Signals
Tests should boot on Hyper-V, validate stimer interrupts, CPU hotplug, suspend/resume or reenlightenment, and non-Hyper-V compile stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hyperv_timer.h -->
