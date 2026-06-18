<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Makefile

Purpose: kbuild composition for the ImgTec IR decoder aggregate module.

Important APIs and entries: `img-ir-y := img-ir-core.o`; optional objects are appended for raw mode, hardware mode, and each enabled hardware protocol decoder. `img-ir-objs := $(img-ir-y)` builds the aggregate object, and `obj-$(CONFIG_IR_IMG) += img-ir.o` adds it to the parent build.

Control flow: kbuild links selected source files into one `img-ir.o`, so the core platform driver and optional raw/hardware/protocol helpers share one module boundary.

State and persistence: no runtime state; object composition only.

Dependencies and integration points: depends on symbols from `img-ir/Kconfig`. The core file expects helper functions from raw/hardware objects to be present or stubbed according to configuration.

Risks: optional protocol objects must stay synchronized with Kconfig names and helper declarations in local headers. Missing an object can produce unresolved symbols only for specific configuration combinations.

Test signals: targeted builds for each `IR_IMG_*` combination and link tests for raw-only, hardware-only, and multi-protocol configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Makefile -->
