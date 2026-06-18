# sources/distributed-fs/ceph-client/arch/arm/probes/Makefile

Purpose: Selects ARM probe decoder and probe subsystem objects for uprobes and kprobes builds.

Important build rules: `CONFIG_UPROBES` builds shared `decode.o`, ARM decoder `decode-arm.o`, and the `uprobes/` subtree. `CONFIG_KPROBES` builds shared `decode.o` and `kprobes/`; it adds `decode-thumb.o` for Thumb-2 kernels and `decode-arm.o` otherwise.

Control flow/integration: Kbuild uses the kernel ISA configuration to pick the correct decoder implementation for kprobes while uprobes always include ARM decode support. The subdirectories provide action/checker implementations consumed by the shared decode tables.

State and risks: No runtime state. Build risk is duplicate or missing decoder objects under mixed `CONFIG_UPROBES`, `CONFIG_KPROBES`, and `CONFIG_THUMB2_KERNEL` configurations. Test with all relevant configuration combinations and link-check probe symbols.
