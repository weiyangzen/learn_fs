<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/Makefile -->
# sources/distributed-fs/ceph-client/tools/gpio/Makefile

Purpose: Builds, cleans, and installs Linux GPIO character-device helper tools: `lsgpio`, `gpio-hammer`, `gpio-event-mon`, and `gpio-watch`.

Important APIs/types/functions: Uses `tools/build/Makefile.include` and per-tool `$(build)=...` invocations. `prepare` symlinks `../../include/uapi/linux/gpio.h` into `$(OUTPUT)include/linux/gpio.h`. `ALL_TARGETS` maps to `ALL_PROGRAMS`; `install` copies binaries to `$(DESTDIR)$(bindir)`.

Control flow: The Makefile computes `srctree` for in-tree or selftest-style builds, disables built-in rules, exports build variables, builds a shared `gpio-utils-in.o` where needed, then links each final tool.

State and persistence: Build artifacts live under `$(OUTPUT)`, including generated include symlink, intermediate `*-in.o` files, `.cmd`/dependency files, and final binaries. `clean` removes binaries, generated include directory, and object/dependency files.

Dependencies/integration: Depends on the kernel tools build system, UAPI GPIO header, C compiler, and standard Linux userspace headers. It can be built inside tools or from selftests.

Risks/tests: Risks include incorrect `srctree` inference, stale symlinked UAPI header, and clean rules deleting unexpected files if `OUTPUT` is unusual. Test signals are in-tree and out-of-tree builds, `make clean`, `make install DESTDIR=...`, and execution against a test gpiochip or mock device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/Makefile -->
