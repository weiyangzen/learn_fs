# sources/distributed-fs/ceph-client/arch/sparc/kernel/entry.h

## Purpose
`entry.h` declares the C/assembly interface for SPARC trap, IRQ, syscall, patching, error, and interrupt-vector paths. It is the shared contract between low-level assembly and C handlers.

## Important APIs, Types, and Functions
Common declaration: `handler_irq()`. The sparc32 side declares trap handlers, `fpsave()`, and `fpload()`. The sparc64 side declares patch entry structs for popcount and pause instructions, sun4v/M7 patch helpers, trap C handlers, fault/error reporters, hypervisor TLB error handlers, `init_irqwork_curcpu()`, `sun4v_register_mondo_queues()`, and the interrupt-vector `struct ino_bucket`.

## Control Flow and State
There is no runtime control flow. The header fixes function signatures and data layouts consumed by assembly. `struct cheetah_err_info` is explicitly layout-sensitive and records AFSR/AFAR plus cache/ecache diagnostic state. `struct ino_bucket` layout is likewise consumed by vector interrupt assembly.

## Persistence and Dependencies
Persistent state declarations include cache parity flags, `cheetah_error_log`, `ivector_table`, and `ivector_table_pa`. The header depends on trap block definitions, architecture offsets, and Linux type/init declarations.

## Integration Points, Risks, and Test Signals
Integration is broad: trap table fragments, C trap handlers, IRQ allocation, hypervisor error reporting, and patching code rely on these exact declarations. Risks include silent ABI breakage if structure fields move without matching hand-coded assembly, incorrect prototype drift, and architecture-config mismatch. Test signals are successful allmodconfig/defconfig builds for sparc32 and sparc64 and boot-time trap/IRQ/error handling on representative sun4u/sun4v hardware or emulation.
