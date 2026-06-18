# sources/distributed-fs/ceph-client/samples/hid/Makefile

Purpose: complex kbuild/userspace build file for HID-BPF samples and skeleton generation.

Important APIs/functions: builds `hid_mouse` and `hid_surface_dial`; builds libbpf and bootstrap bpftool under sample-local output directories; generates `vmlinux.h`, BPF objects, linked BPF skeleton headers, and user objects. Probes LLVM/BTF capabilities and adds architecture-specific flags.

Control flow: kbuild invokes libbpf/bpftool prerequisites, validates LLVM BPF target, emits BPF bytecode with clang/opt/llc, generates skeletons with bpftool, then links user programs with libbpf, elf, and zlib.

State and persistence: generated build artifacts under the sample object tree, `libbpf/`, `bpftool/`, `vmlinux.h`, `.bpf.o`, `.skel.h`, and user binaries.

Dependencies and integration: depends on kernel BTF or `VMLINUX_H`, LLVM BPF backend, bpftool, libbpf, libelf, zlib, and architecture include quirks.

Risks: fragile toolchain detection, generated artifact cleanup requirements, and cross-compile include issues. Build reaches into kernel tools and selftests include paths.

Test signals: `make samples/hid/` should build skeletons and two user programs; missing BTF or LLVM target should fail with explicit errors.
