<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/image.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/image.h

## Purpose
Defines the RISC-V boot image header, magic values, flags, version, and load metadata.

## Important APIs, Types, And Functions
types `riscv_image_header`; macros/constants `_ASM_RISCV_IMAGE_H`, `RISCV_IMAGE_MAGIC`, `RISCV_IMAGE_MAGIC2`, `RISCV_IMAGE_FLAG_BE_SHIFT`, `RISCV_IMAGE_FLAG_BE_MASK`, `RISCV_IMAGE_FLAG_LE`, `RISCV_IMAGE_FLAG_BE`, `__HEAD_FLAG_BE`, `__HEAD_FLAG(field)`, `__HEAD_FLAGS`, `RISCV_HEADER_VERSION_MAJOR`, `RISCV_HEADER_VERSION_MINOR`, `RISCV_HEADER_VERSION`, `riscv_image_flag_field(flags, field)`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 67 lines, 1775 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/image.h -->
