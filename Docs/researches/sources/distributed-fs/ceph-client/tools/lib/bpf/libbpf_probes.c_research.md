<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_probes.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_probes.c

## Purpose
This implementation probes host-kernel BPF capabilities by attempting small BPF program loads, map creations, and BTF loads. It also derives kernel version codes for kernels where `uname()` does not match the version expected by BPF program loading.

## APIs, Types, and Functions
Kernel version helpers are `get_ubuntu_kernel_version()`, `get_debian_kernel_version()`, and public internal `get_kernel_version()`. Program probing is built around `probe_prog_load()` and exported as `libbpf_probe_bpf_prog_type()` and `libbpf_probe_bpf_helper()`. Raw BTF helpers `libbpf__load_raw_btf_hdr()` and `libbpf__load_raw_btf()` construct a BTF blob and call `bpf_btf_load()`. `load_local_storage_btf()` creates a minimal BTF schema for local-storage map probes. `probe_map_create()` covers map-type-specific key/value/max_entries/options setup and is exported as `libbpf_probe_bpf_map_type()`.

## Control Flow, State, and Persistence
`get_kernel_version()` first tries `/proc/version_signature` for Ubuntu, then Debian `utsname.version`, then `utsname.release`, returning a `KERNEL_VERSION()` code or zero. `probe_prog_load()` builds minimal instructions, configures expected attach type or special expected failure cases for tracing, LSM, EXT, syscall, struct_ops, and kprobes, calls `bpf_prog_load()`, closes any successful FD, and returns `1` for supported, `0` for unsupported, or a negative error for unsupported input. `probe_map_create()` selects valid dimensions and flags per map type, creates inner maps or temporary BTF where required, calls `bpf_map_create()`, closes all created FDs, and treats selected expected errors as support signals. `libbpf_probe_bpf_helper()` loads a two-instruction program calling the helper and interprets verifier logs containing invalid/unknown helper messages as lack of support; other verifier errors are treated as likely support.

State is transient: FDs for programs, maps, inner maps, and BTF are closed before return. The only external state read is `/proc/version_signature` and `uname()`. Probes can consume kernel resources temporarily and rely on privileges/capabilities.

## Dependencies and Integration
The file depends on `bpf.h` syscall wrappers, `libbpf.h`, `libbpf_internal.h`, Linux BTF/filter/kernel/version headers, libc file and uname APIs, and network interface definitions. It feeds internal feature checks and public probe APIs declared in `libbpf.h`.

## Risks and Test Signals
Risks include false negatives without CAP_BPF/CAP_SYS_ADMIN or sufficient memlock, kernel verifier message changes affecting helper detection, distro version parsing drift, expected-error matching for special program/map types, temporary BTF layout compatibility, and probes failing under constrained containers. Test signals include controlled unit tests for distro version parsing, integration tests on kernels with known map/prog/helper support matrices, verifier-log pattern tests, FD leak checks, and privilege-denied behavior distinguishing unsupported features from execution failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_probes.c -->
