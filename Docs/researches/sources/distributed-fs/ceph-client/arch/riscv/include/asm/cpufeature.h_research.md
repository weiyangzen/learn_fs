<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature.h

## Purpose
Declares CPU and ISA feature discovery state, extension descriptors, unaligned-access probing, and ELF hwcap export helpers.

## Important APIs, Types, And Functions
types `riscv_cpuinfo`, `riscv_isainfo`, `seq_operations`, `work_struct`, `riscv_isa_ext_data`; functions/prototypes `unaligned_access_init`, `cpu_online_unaligned_access_init`, `unaligned_emulation_finish`, `unaligned_ctl_available`, `misaligned_traps_can_delegate`, `check_vector_unaligned_access_emulated`, `has_fast_unaligned_accesses`, `riscv_get_elf_hwcap`, `riscv_isa_extension_base`, `riscv_cpu_has_extension_likely`, `riscv_cpu_has_extension_unlikely`, `cpu_supports_shadow_stack`, plus 5 more; macros/constants `_ASM_CPUFEATURE_H`, `_RISCV_ISA_EXT_DATA(_name, _id, _subset_exts, _subset_exts_size, _validate)`, `__RISCV_ISA_EXT_DATA(_name, _id) _RISCV_ISA_EXT_DATA(_name, _id, NULL, 0, NULL)`, `__RISCV_ISA_EXT_DATA_VALIDATE(_name, _id, _validate)`, `__RISCV_ISA_EXT_BUNDLE(_name, _bundled_exts)`, `__RISCV_ISA_EXT_BUNDLE_VALIDATE(_name, _bundled_exts, _validate)`, `__RISCV_ISA_EXT_SUPERSET(_name, _id, _sub_exts)`, `__RISCV_ISA_EXT_SUPERSET_VALIDATE(_name, _id, _sub_exts, _validate)`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/bitmap.h`, `linux/jump_label.h`, `linux/workqueue.h`, `linux/kconfig.h`, `linux/percpu-defs.h`, `linux/threads.h`, `asm/hwcap.h`, `asm/cpufeature-macros.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 167 lines, 4991 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature.h -->
