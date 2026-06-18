# sources/distributed-fs/ceph-client/tools/testing/selftests/net/Makefile

Purpose: Top-level build and run manifest for a broad set of networking selftests.

Important APIs/types/functions: Sets common `CFLAGS`, kernel header includes, `TEST_PROGS` shell/Python test scripts, `TEST_GEN_FILES` compiled helper binaries, `TEST_GEN_PROGS` harness binaries, `TEST_FILES`, YNL generation variables, target-specific `LDLIBS`/`CFLAGS`, and includes `../lib.mk`, `ynl.mk`, and `bpf.mk`.

Control flow: Kselftest `lib.mk` builds generated programs/files and arranges runnable scripts. The YNL section adds generated netlink tools (`busy_poller`, `netlink-dumps`, `tun`) before including `ynl.mk`. The final `include bpf.mk` builds BPF object files from `*.bpf.c`.

State and persistence behavior: Build outputs are placed under `$(OUTPUT)`. The Makefile itself is declarative and does not create runtime network state.

Dependencies and integration points: Coordinates many scripts in this subset (`altnames.sh`, `amt.sh`, `bareudp.sh`, `big_tcp.sh`, `bind_bhash.sh`, `bpf_offload.py`, bridge tests, broadcast tests, `busy_poll_test.sh`) and C programs (`bind_bhash`, `bind_timewait`, `bind_wildcard`). It also connects to kselftest forwarding library files and BPF/YNL build support.

Risks: Large manifests can drift when source files are added/removed. Some generated programs need optional libraries (`libcap`, `libnuma`, `pthread`, `crypto`), and missing dependencies surface at build time. BPF object generation depends on `clang`, libbpf, and kernel UAPI headers.

Test signals: A successful `make` in `tools/testing/selftests/net` builds all listed generated files and exposes scripts for `run_kselftest.sh`. Missing toolchain or library problems usually fail named target builds.
