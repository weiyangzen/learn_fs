# sources/distributed-fs/ceph-client/tools/verification/rv/Makefile

Purpose: this Makefile builds the `rv` userspace tool for the Linux runtime verification subsystem.

Important variables and targets: it derives `srctree`, handles `O=`/`OUTPUT`, sets `RV` and `RV_IN`, computes `VERSION` from the kernel top-level makefile, and points `DOCSRC` to RV tool docs. Feature tests require/display `libtraceevent` and `libtracefs`. It includes tools build infrastructure, `Makefile.rv`, feature detection, and `Makefile.config`. `$(RV)` links `rv-in.o` with `$(EXTLIBS)`, `static` builds `rv-static`, pattern `rv.%` and `$(RV_IN)` delegate to `tools/build`, and `clean` removes objects, feature dumps, and generated binaries.

Control flow and integration: the Makefile is meant to be invoked from the kernel tools build system or directly. It exports build variables for sub-make and avoids dependency configuration for non-build targets such as clean/install/doc.

State, dependencies, risks, and tests: generated state lives under `OUTPUT`. Dependencies include kernel tools build scripts, libtraceevent, libtracefs, and compiler/linker settings. Risks include relative srctree assumptions, dependency-feature drift, and output path normalization errors. Test signals are successful `make`, `make static`, feature detection, and `./rv list` running on a kernel with CONFIG_RV.
