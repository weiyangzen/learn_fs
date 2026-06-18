# sources/distributed-fs/ceph-client/tools/power/x86/x86_energy_perf_policy/Makefile

Purpose: builds and packages the `x86_energy_perf_policy` utility, a privileged x86 power-policy tool. It supports normal in-tree builds, `O=` redirected builds, installation into `$(DESTDIR)$(PREFIX)`, cleanup, and a snapshot tarball that carries enough copied kernel headers to build outside the kernel tree.

Important APIs and targets: `CC=$(CROSS_COMPILE)gcc`, `BUILD_OUTPUT`, `PREFIX`, `DESTDIR`, and `SNAPSHOT` are the main variables. The explicit `x86_energy_perf_policy : x86_energy_perf_policy.c` dependency is built by the generic `%: %.c` rule. `override CFLAGS` adds optimization, warnings, the tools include path, `MSRHEADER` pointing at `arch/x86/include/asm/msr-index.h`, and `_FORTIFY_SOURCE=2`. Targets are `clean`, `install`, and `snapshot`.

Control flow: `all` is implicit through the first target. The pattern rule creates the output directory and invokes the compiler. `install` first builds the tool, then installs the binary and man page. `snapshot` removes any same-day staging directory, copies the sources and man page, rewrites `msr-index.h` include assumptions, emits compatibility `bits.h` and `build_bug.h`, writes a standalone Makefile, and archives the snapshot.

State and persistence: build artifacts land in `$(BUILD_OUTPUT)`, which defaults to the source directory and switches to `$(O)` when `O=` is supplied. `install` persists under `$(DESTDIR)$(PREFIX)`. `snapshot` creates and replaces date-stamped directories and `.tar.gz` files in the working directory.

Dependencies and integration: depends on kernel tools make infrastructure only indirectly through include paths and the x86 `msr-index.h` header. Snapshot mode deliberately removes that dependency by copying and rewriting header fragments. Runtime dependencies of the built tool are in the C source, not the Makefile.

Risks: the `snapshot` target performs broad `rm -rf $(SNAPSHOT)` and `rm -f $(SNAPSHOT).tar.gz` operations based on a generated date name. The MSR header path is relative and fragile if the tool moves. `install` assumes `x86_energy_perf_policy.8` exists beside the Makefile.

Test signals: successful `make`, `make O=/tmp/out`, `make install DESTDIR=/tmp/stage`, and `make snapshot` are the relevant checks. Compile should fail quickly if `MSRHEADER` or kernel include paths are wrong.
