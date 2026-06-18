<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_stack.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_stack.h

## Purpose
Declares IRQ-stack switching and vmapped IRQ-stack allocation helpers.

## Important APIs, Types, And Functions
types `pt_regs`; functions/prototypes `call_on_irq_stack`, `arch_alloc_vmap_stack`; macros/constants `_ASM_RISCV_IRQ_STACK_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/bug.h`, `linux/gfp.h`, `linux/kconfig.h`, `linux/vmalloc.h`, `linux/pgtable.h`, `asm/thread_info.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 33 lines, 843 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_stack.h -->
