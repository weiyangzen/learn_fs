<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwprobe.h

## Purpose
Declares kernel-side helpers for the RISC-V `hwprobe` syscall key validation, sorting, and asynchronous probing.

## Important APIs, Types, And Functions
types `riscv_hwprobe`; functions/prototypes `riscv_hwprobe_key_is_valid`, `hwprobe_key_is_bitmask`, `riscv_hwprobe_pair_cmp`, `riscv_hwprobe_register_async_probe`, `riscv_hwprobe_complete_async_probe`; macros/constants `_ASM_HWPROBE_H`, `RISCV_HWPROBE_MAX_KEY`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `uapi/asm/hwprobe.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 53 lines, 1288 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwprobe.h -->
