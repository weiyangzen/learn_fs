<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/elf.h

## Purpose
Defines the RISC-V ELF ABI hooks, hwcap/auxv export, core-reg copying, compat ELF checks, and personality setup.

## Important APIs, Types, And Functions
types `linux_binprm`, `user_regs_struct`; functions/prototypes `compat_elf_check_arch`, `arch_setup_additional_pages`, `compat_arch_setup_additional_pages`, `elf_hwcap`; macros/constants `_ASM_RISCV_ELF_H`, `ELF_ARCH`, `ELF_CLASS`, `ELF_DATA`, `elf_check_arch(x) (((x)->e_machine == EM_RISCV)`, `compat_elf_check_arch`, `CORE_DUMP_USE_REGSET`, `ELF_FDPIC_CORE_EFLAGS`, `ELF_EXEC_PAGESIZE`, `ELF_ET_DYN_BASE`, `STACK_RND_MASK`, `ELF_HWCAP`, `ELF_FDPIC_PLAT_INIT(_r, _exec_map_addr, _interp_map_addr, dynamic_addr)`, `ELF_PLATFORM`, plus 7 more.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `uapi/linux/elf.h`, `linux/compat.h`, `uapi/asm/elf.h`, `asm/auxvec.h`, `asm/byteorder.h`, `asm/cacheinfo.h`, `asm/cpufeature.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 156 lines, 4748 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/elf.h -->
