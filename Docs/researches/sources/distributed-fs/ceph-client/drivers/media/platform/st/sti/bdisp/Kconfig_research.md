# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/Kconfig

Purpose: defines the Kconfig symbol for the STMicroelectronics BDISP 2D blitter V4L2 mem2mem driver.

Important APIs and symbols: `VIDEO_STI_BDISP` is a tristate depending on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_STI || COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

Control flow: enabling this symbol causes the BDISP Makefile to build the BDISP module/object from V4L2, hardware, and debug components.

State and persistence: no runtime state. The symbol persists in kernel configuration and determines module availability.

Dependencies and integration points: integrates BDISP with the V4L2 mem2mem framework, video device core, and contiguous videobuf2 DMA allocator on STi SoCs or compile-test builds.

Risks: missing dependencies for clocks, reset, runtime PM, or debugfs would surface only at build/link time if used by implementation files. Compile-test support increases coverage but may expose architecture assumptions.

Test signals: Kconfig visibility, allmodconfig, COMPILE_TEST builds, and runtime module load on ARCH_STI platforms.
