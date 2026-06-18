# sources/distributed-fs/ceph-client/tools/counter/Makefile

Purpose: Builds and installs userspace counter examples `counter_example` and `counter_watch_events`.

Important APIs, types, and functions: Defines `ALL_TARGETS`, `ALL_PROGRAMS`, CFLAGS with generated include directory and kernel tools include, `prepare` symlink for `linux/counter.h`, per-target object and link rules, `clean`, and `install`.

Control flow: `all` depends on output programs. `prepare` creates `$(OUTPUT)include/linux/counter.h` symlink from kernel UAPI. Each object invokes `tools/build`, then links with `$(CC)`. Install copies programs to `$(DESTDIR)$(bindir)`.

State and persistence: Creates output binaries, object files, generated dependency files, and a symlinked UAPI header under `$(OUTPUT)include`.

Dependencies and integration points: Uses kernel tools build system and UAPI `include/uapi/linux/counter.h`. Intended for in-tree and out-of-tree tools builds.

Risks: Header symlink assumes relative path from tools/counter. Clean removes `$(OUTPUT)include` and object/dependency files. Build depends on `OUTPUT` semantics from tools environment.

Test signals: `make`, `make OUTPUT=/tmp/...`, `make install DESTDIR=...`, and `make clean`.
