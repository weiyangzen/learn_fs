<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/feature.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/feature.c

Purpose: this implements `bpftool feature`, including kernel/device feature probing and listing libbpf-known built-in program, map, attach, link, and helper names.

Important APIs/functions: printing helpers include `print_bool_feature()`, `print_kernel_option()`, and section start/end functions for plain, JSON, or C macro output. Probes include procfs sysctl readers, `probe_kernel_image_config()`, `probe_bpf_syscall()`, program/map type probing, helper probing, and miscellaneous instruction-set/prog-size probes. `handle_perms()` validates or drops capabilities for privileged/unprivileged probing. `do_probe()` parses options and runs all sections; `do_list_builtins()` prints built-in name lists.

Control flow: `do_feature()` dispatches `probe`, `list_builtins`, and `help`. Probe parsing accepts optional `kernel` or `dev NAME`, `full`, `unprivileged`, and `macros [prefix PREFIX]`. It raises memlock limits as needed, checks permissions/capabilities, starts JSON root if requested, scans system config, tests `bpf()` syscall availability, and only then probes program types, map types, helpers, and miscellaneous features. Device probing restricts program and map probes to offload-relevant types and uses `prog_ifindex`/`map_ifindex`.

State and persistence: probing can load short BPF programs and create maps transiently, closing FDs immediately. With libcap and `unprivileged`, it can drop effective capabilities in the running process. It reads procfs, sysfs, and kernel config files but does not persist configuration changes. Static state includes `full_mode` and optionally `run_as_unprivileged`.

Dependencies and integration points: it depends on libbpf probe helpers, BPF syscalls, `common.c` for memlock/kernel config support, optional libcap, procfs, sysfs netdevice vendor files, and bpftool JSON output. Macro output is intended for build-time feature gating in external BPF code.

Risks: probes are sensitive to permissions, LSM policy, lockdown, kernel config availability, backports, and offload driver behavior. Helper probing in non-full mode intentionally skips helpers that can emit dmesg messages. `probe_misc_feature()` treats `fd >= 0 || !errno` as success, so unusual libbpf errno behavior can affect results. Fixed `supported_types[128]` assumes program type values fit. Device vendor-specific helper log parsing currently special-cases Netronome. Capability handling differs when bpftool is built without libcap.

Test signals: tests should cover plain/json/macro output, macro prefixes, kernel-only and device-only probes, unprivileged mode with libcap, missing procfs, missing kernel config, missing capabilities, helper skip behavior with and without `full`, list_builtins groups, and expected behavior on kernels without BPF syscall or specific feature support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/feature.c -->
