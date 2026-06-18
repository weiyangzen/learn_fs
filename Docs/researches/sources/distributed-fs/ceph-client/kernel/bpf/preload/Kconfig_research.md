# sources/distributed-fs/ceph-client/kernel/bpf/preload/Kconfig

Purpose: defines Kconfig options for building the BPF preload facility that embeds kernel-specific BPF iterator programs and pins useful introspection links into bpffs. The source was read as a complete 21-line file.

Important APIs/options: `menuconfig BPF_PRELOAD` and `config BPF_PRELOAD_UMD`. `BPF_PRELOAD` depends on `BPF`, `BPF_SYSCALL`, and `!COMPILE_TEST`; `BPF_PRELOAD_UMD` is a tristate defaulting to module.

Control flow: no runtime flow. Kconfig controls whether the preload module is built and whether embedded iterator programs are available.

State and persistence: build-time configuration only. Runtime persistence comes from the module and bpffs links described in companion files.

Dependencies/integration: integrates with kernel Kconfig, BPF syscall availability, and module build rules in the preload Makefile. `!COMPILE_TEST` prevents broad allmodconfig/allyesconfig enablement.

Risks and edge cases: enabling depends on BPF syscall support and generated skeleton compatibility. Default module build means missing module load prevents bpffs debug files from appearing.

Test signals: Kconfig dependency tests, allmodconfig behavior, module build/load checks, and bpffs introspection file presence.
