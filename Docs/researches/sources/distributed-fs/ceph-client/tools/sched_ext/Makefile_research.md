# sources/distributed-fs/ceph-client/tools/sched_ext/Makefile

Purpose: builds sched_ext C example schedulers and their BPF struct_ops programs. It handles libbpf, bpftool, `vmlinux.h` generation, BPF object linking, skeleton/subskeleton generation, final C loader binaries, installation, cleanup, and help text.

Important APIs/variables/targets: includes tools build infrastructure and architecture makefiles. Key paths are `OUTPUT_DIR`, `OBJ_DIR`, `INCLUDE_DIR`, `BPFOBJ_DIR`, `SCXOBJ_DIR`, `BINDIR`, `BPFOBJ`, `HOST_BPFOBJ`, `RESOLVE_BTFIDS`, and `DEFAULT_BPFTOOL`. `VMLINUX_BTF_PATHS` searches build outputs, `../../vmlinux`, `/sys/kernel/btf/vmlinux`, and `/boot/vmlinux-$(uname -r)`. `BPF_CFLAGS` sets target arch, endian, include paths, system include fallbacks, and `-target bpf` compile flags. `c-sched-targets` lists produced schedulers.

Control flow: the default target builds `all_targets`. The Makefile selects clang when `LLVM` is set and derives target flags for cross compilation. It builds host and target libbpf as needed, builds bpftool, generates `vmlinux.h`, compiles each `%.bpf.c` into a BPF object, runs bpftool link stabilization and `diff` on linked objects, emits skeleton headers, then compiles each user-space `%.c` loader and links it with libbpf. `install` copies binaries under `/usr/local/bin` in `DESTDIR`.

State and persistence: all generated artifacts are under `build/` by default or `$(O)/build`. Generated skeleton headers and `vmlinux.h` live under the output include directory. `clean` removes output trees and stray root-level generated files.

Dependencies and integration: depends on clang for BPF, libelf, zlib, pthread, libbpf sources under `tools/lib/bpf`, bpftool under `tools/bpf/bpftool`, generated kernel headers when available, and a discoverable vmlinux BTF source. It integrates the headers in `include/scx` and includes `include/bpf-compat` to paper over distro header issues for BPF builds.

Risks: hard failure if no `VMLINUX_BTF` is found. Cross builds have separate host/target libbpf paths and can fail if host tools are unavailable. `get_sys_includes` depends on compiler diagnostic format. The skeleton generation assumes repeated bpftool linking converges and verifies it with `diff`.

Test signals: `make help`, `make LLVM=1`, individual scheduler targets, `O=/tmp/sched_ext make all`, missing-vmlinux failure, cross compile with `CROSS_COMPILE`, and successful execution of built schedulers are the primary signals.
