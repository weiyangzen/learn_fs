# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/timer-sr.c

## Purpose
This file provides the VHE hyp helper for programming the virtual counter offset register.

## Important APIs, Types, and Functions
- `__kvm_timer_set_cntvoff(u64 cntvoff)` writes `cntvoff_el2`.

## Control Flow
There is one direct control path: callers pass the desired virtual counter offset and the helper writes it to the EL2 register.

## State and Persistence
The only persistent state touched is hardware `CNTVOFF_EL2`. It affects the virtual counter view observed by guests.

## Dependencies and Integration Points
It depends on `asm/kvm_hyp.h` and is built into the VHE hyp object set. It integrates with ARM generic timer virtualization and world-switch timer state management in the wider KVM timer code.

## Risks and Edge Cases
Incorrect offset programming changes guest time. The helper intentionally does not add policy, validation, or barriers; callers must sequence it with timer context management.

## Test Signals
Guest clocksource stability tests, PV time tests, migration timekeeping tests, and repeated vCPU scheduling with changing offsets should expose regressions.
