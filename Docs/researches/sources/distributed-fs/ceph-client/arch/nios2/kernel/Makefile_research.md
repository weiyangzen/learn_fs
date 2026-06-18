# sources/distributed-fs/ceph-client/arch/nios2/kernel/Makefile

Purpose: selects the Nios II kernel objects for build, including entry, traps, setup, process, signal,
syscall, IRQ, time, module, CPU info, and optional KGDB/alignment trap support.

Important APIs/types/functions: Build declarations: `obj-y=head.o`, `obj-y=cpuinfo.o`, `obj-y=entry.o`, `obj-y=insnemu.o`,
`obj-y=irq.o`, `obj-y=nios2_ksyms.o`, `obj-y=process.o`, `obj-y=prom.o`, `obj-y=ptrace.o`,
`obj-y=setup.o`, `obj-y=signal.o`, `obj-y=sys_nios2.o`, `obj-y=syscall_table.o`, `obj-y=time.o`,
`obj-y=traps.o`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
