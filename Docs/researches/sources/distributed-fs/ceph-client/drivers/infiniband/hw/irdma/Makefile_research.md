# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/Makefile

Purpose: build recipe for the Intel irdma RDMA driver. It maps `CONFIG_INFINIBAND_IRDMA` to the composite `irdma.o` module and lists all translation units that make up the driver.

Important entries: `obj-$(CONFIG_INFINIBAND_IRDMA) += irdma.o` controls inclusion. `irdma-objs` includes connection management (`cm.o`), control/HMC/hardware setup, generation-specific i40iw and ig3rdma/icrdma files, main device registration, PBLE, PUDA, trace, UDA, user/kernel verbs, utilities, virtchnl, and work scheduler code. `CFLAGS_trace.o = -I$(src)` ensures trace compilation can include local generated/header paths.

Control flow: Kbuild compiles each object in `irdma-objs` and links them into one built-in or module object according to Kconfig. The object order expresses broad dependencies but runtime initialization is still controlled by module/device code.

State and persistence: no runtime state; this file determines compile/link composition.

Dependencies and integration: integrates with Linux Kbuild and the RDMA hardware driver directory. Its object list must remain synchronized with internal headers and exported functions across irdma source files.

Risks: missing an object yields unresolved symbols or silently absent feature paths. Adding a new trace user may require CFLAGS/header updates. Whitespace alignment is mixed tabs/spaces but acceptable to make.

Test signals: incremental and clean kernel builds, `modpost` symbol checks, build with `INFINIBAND_IRDMA=m` and `=y`, and tracepoint compilation.
