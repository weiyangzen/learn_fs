<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwcap.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwcap.h

## Purpose
Enumerates RISC-V ISA extension IDs and bitmap sizing used by cpufeature, alternatives, KVM, and userspace hwcap reporting.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_HWCAP_H`, `RISCV_ISA_EXT_a`, `RISCV_ISA_EXT_c`, `RISCV_ISA_EXT_d`, `RISCV_ISA_EXT_f`, `RISCV_ISA_EXT_h`, `RISCV_ISA_EXT_i`, `RISCV_ISA_EXT_m`, `RISCV_ISA_EXT_q`, `RISCV_ISA_EXT_v`, `RISCV_ISA_EXT_BASE`, `RISCV_ISA_EXT_SSCOFPMF`, `RISCV_ISA_EXT_SSTC`, `RISCV_ISA_EXT_SVINVAL`, plus 82 more.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Special attention: extension IDs are shared by cpufeature, alternatives, KVM ISA exposure, ELF hwcaps, and hwprobe reporting; gaps and numbering are compatibility-sensitive.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `uapi/asm/hwcap.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 129 lines, 4081 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwcap.h -->
