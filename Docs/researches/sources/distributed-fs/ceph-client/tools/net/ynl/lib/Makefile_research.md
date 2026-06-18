# sources/distributed-fs/ceph-client/tools/net/ynl/lib/Makefile

Purpose: Builds the reusable C YNL runtime library objects into `ynl.a`.

Important targets and variables: `SRCS` is all local `*.c`, `OBJS` maps those to object files, and generated dependency files `*.d` are included when present. `CFLAGS` select GNU11, optimization, warnings, and optional AddressSanitizer/LeakSanitizer when `DEBUG=1`.

Control flow: The default `all` target builds `ynl.a` from all objects. The `%.o: %.c` rule compiles with `-MMD` so dependency files are emitted next to objects. `clean` removes objects, dependency files, and editor backups; `distclean` additionally removes the archive.

Dependencies and integration: The top-level YNL Makefile consumes `lib/ynl.o` directly for `libynl.a`, while this local archive is useful for standalone consumers and subdirectory builds.

State and persistence: Produces object files, dependency files, and `ynl.a`; no runtime state.

Risks: `SRCS=$(wildcard *.c)` means any new C file is automatically linked into the archive. Sanitizer flags add `-static-libasan`, which can fail on toolchains lacking the static ASan runtime. There is no explicit header install here; header installation is handled by the parent Makefile.

Test signals: Build with default flags and `DEBUG=1`, touch headers to confirm `.d` dependencies rebuild, run `clean` and `distclean`, and verify top-level `libynl.a` still picks up `ynl.o`.
