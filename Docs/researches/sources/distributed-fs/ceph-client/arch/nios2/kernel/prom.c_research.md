# sources/distributed-fs/ceph-client/arch/nios2/kernel/prom.c

Purpose: performs early devicetree initialization for Nios II from the bootloader-provided blob.

Important APIs/types/functions: functions: `Copyright`; prototypes: `early_init_dt_scan`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/init.h`, `linux/types.h`, `linux/memblock.h`, `linux/of.h`,
`linux/of_fdt.h`, `linux/io.h`, `asm/sections.h`. Integration points include generic Linux MM, irq,
signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
