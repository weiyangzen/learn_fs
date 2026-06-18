# sources/distributed-fs/ceph-client/tools/net/ynl/tests/Makefile

Purpose: builds and installs YNL selftests and helper demos. It compiles C tests against `../lib/ynl.a` and `../generated/protos.a`, exposes shell wrappers as `TEST_PROGS`, and installs into the kselftest layout.

Important build variables: `CFLAGS` enables GNU11, warnings, shadow checks, YNL/lib/generated include paths, selftest headers, and UAPI include fallback. Unless `NDEBUG=1`, address and leak sanitizers plus debug info are enabled. `LDLIBS` links the generated protocol archive and YNL runtime.

Control flow: `all` builds `TEST_GEN_PROGS` (`netdev`, `ovs`, `rt-link`, `tc`) and `TEST_GEN_FILES` (`devlink`, `ethtool`, `rt-addr`, `rt-route`). Pattern rules compile each `%.c` to `%.o` then link. `run_tests` executes shell tests. `install` copies binaries, helper Python/shell files, rewrites wrapper paths for installed tools, and emits `kselftest-list.txt`.

Dependencies/integration: includes `../Makefile.deps`, depends on generated protocol headers, kselftest `ktap_helpers.sh`, and target kernel features described by `tests/config`.

Risks/test signals: sanitizer/static-libasan may fail on hosts without the runtime. Generated header drift breaks compile quickly. Install path rewriting must stay aligned with wrapper variable names. The primary signal is `make -C tools/net/ynl/tests run_tests` or kselftest execution under a kernel with required networking modules.
