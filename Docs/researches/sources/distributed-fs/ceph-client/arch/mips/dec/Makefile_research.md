# sources/distributed-fs/ceph-client/arch/mips/dec/Makefile

Purpose: selects DECstation platform support objects for the MIPS build.

Important build behavior: always builds bus-error handlers, interrupt handler assembly, I/O ASIC IRQ support, KN02 CSR IRQ support, platform devices, reset, setup, and time. TurboChannel support `tc.o` depends on `CONFIG_TC`; write-buffer flushing support `wbflush.o` depends on `CONFIG_CPU_HAS_WB`.

Dependencies and integration: this Makefile binds architecture setup, PROM support, IRQ controllers, and optional buses to the kernel image.

Risks and test signals: omitting optional objects under the wrong config can break buses or required barriers. Build matrix should include DECstation with TurboChannel and write-buffer-capable CPU configs.
