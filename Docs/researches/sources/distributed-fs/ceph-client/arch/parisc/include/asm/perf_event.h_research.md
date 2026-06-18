# sources/distributed-fs/ceph-client/arch/parisc/include/asm/perf_event.h

Purpose: connects PA-RISC to the generic perf event framework.

Important APIs/types/functions: declares architecture perf initialization hooks or maps to generic defaults when hardware support is limited.

Control flow: perf core calls architecture hooks during event creation, scheduling, reading, and overflow handling.

State and persistence: active perf events and hardware counter assignments persist while events are scheduled. Dependencies and integration: depends on `perf.h`, IRQ handling, and generic perf_event code.

Risks and test signals: incomplete hooks should fail cleanly rather than expose bogus counters. Test with perf list/stat/record and unsupported-event error paths.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
