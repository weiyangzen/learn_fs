<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/dslm/Makefile -->
# sources/distributed-fs/ceph-client/tools/laptop/dslm/Makefile

Purpose: this small Makefile builds the `dslm` disk sleep monitor utility.

Important APIs/targets: it sets `CC := $(CROSS_COMPILE)gcc`, `CFLAGS := -I../../usr/include`, `PROGS := dslm`, and defines `all` plus `clean`.

Control flow: default `all` builds `dslm` through make's implicit C compilation rule. `clean` removes the program.

State and persistence: generated state is the `dslm` executable in the source directory.

Dependencies/integration: depends on a C compiler, optional `CROSS_COMPILE`, and headers under `../../usr/include` including Linux hdreg definitions used by `dslm.c`.

Risks and test signals: risk is relying on implicit rules and local kernel headers. Test `make`, `make clean`, and cross-compile variable propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/dslm/Makefile -->
