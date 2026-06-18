# sources/distributed-fs/openafs/src/bozo/test/Makefile.in

This makefile builds the `testproc` helper used for bos/bnode process supervision tests. It includes the top-level OpenAFS make configuration and defines `all`, `testproc`, `clean`, empty `install`, and empty `dest` targets.

The only build API is the `testproc: testproc.c` rule, invoking `$(CC)` with `$(AFS_LDFLAGS)` and `$(AFS_CFLAGS)`. No libraries are linked beyond the platform defaults implied by compiler flags.

There is no runtime state. Persistence is limited to generated `testproc`, object/core files, and clean removal. Dependencies are the configured compiler variables and `testproc.c`. Risks are low, but `MODULE_CFLAGS=$(LDIRS) $(LIBS)` appears unused and install/dest intentionally do nothing, so downstream tests must run from the build directory. Test signals are successful build and `make clean` removing generated artifacts.
