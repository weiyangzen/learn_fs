<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/compat.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/compat.h

## Purpose
Defines 32-bit compat task detection and register conversion helpers for 64-bit kernels running RV32 userspace.

## Important APIs, Types, And Functions
types `thread_info`, `compat_user_regs_struct`, `pt_regs`; functions/prototypes `is_compat_task`, `is_compat_thread`, `set_compat_task`, `regs_to_cregs`, `cregs_to_regs`; macros/constants `__ASM_COMPAT_H`, `COMPAT_UTS_MACHINE`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `linux/sched.h`, `asm-generic/compat.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 147 lines, 4152 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/compat.h -->
