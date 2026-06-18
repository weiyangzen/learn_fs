<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature-macros.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature-macros.h

## Purpose
Provides static-key/alternative aware helpers for fast RISC-V ISA extension tests.

## Important APIs, Types, And Functions
functions/prototypes `__riscv_isa_extension_available`, `__riscv_has_extension_likely`, `__riscv_has_extension_unlikely`, `riscv_has_extension_unlikely`, `riscv_has_extension_likely`; macros/constants `_ASM_CPUFEATURE_MACROS_H`, `STANDARD_EXT`, `riscv_isa_extension_available(isa_bitmap, ext)`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/hwcap.h`, `asm/alternative-macros.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 66 lines, 1706 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature-macros.h -->
