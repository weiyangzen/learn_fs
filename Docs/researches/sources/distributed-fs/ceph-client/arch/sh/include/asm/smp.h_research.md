<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/smp.h

## Purpose
Defines SH architecture declarations and macros for `smp` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/bitops.h`, `linux/cpumask.h`, `asm/smp-ops.h`, `linux/atomic.h`, `asm/current.h`, `asm/percpu.h`. Key macros/constants include `__ASM_SH_SMP_H`, `raw_smp_processor_id()`, `cpu_number_map(cpu)`, `cpu_logical_map(cpu)`, `CPU_METHOD_OF_DECLARE(name, _method, _ops)`, `hard_smp_processor_id()`. Structures include `of_cpu_method`, `plat_smp_ops`. Functions or extern declarations include `smp_message_recv`, `arch_send_call_function_single_ipi`, `arch_send_call_function_ipi_mask`, `native_play_dead`, `native_cpu_die`, `native_cpu_disable`, `play_dead_common`, `__cpu_disable`, `mp_ops`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/bitops.h`, `linux/cpumask.h`, `asm/smp-ops.h`, `linux/atomic.h`, `asm/current.h`, `asm/percpu.h`. Kconfig-sensitive paths mention `CONFIG_SMP`, `CONFIG_HOTPLUG_CPU`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 83 lines, 1847 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/smp.h -->
