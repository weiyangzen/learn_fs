## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputable.h

Purpose: defines the central PowerPC CPU specification structure, CPU feature bitmasks, per-family feature sets, possible/always feature masks, and CPU identification/fixup interfaces.

Important APIs/types/functions: `struct cpu_spec` records PVR match fields, feature masks, cache sizes, CPU setup/restore callbacks, platform names, and machine-check handlers. It declares `cur_cpu_spec`, `identify_cpu()`, `set_cur_cpu_spec()`, `identify_cpu_name()`, `do_feature_fixups()`, machine-check handlers, and `cpu_feature_keys_init()`. Feature macros include common bits such as `CPU_FTR_ALTIVEC`, `CPU_FTR_LWSYNC`, `CPU_FTR_DBELL`, POWER architecture levels, errata flags, and per-family `CPU_FTRS_*` bundles.

Control flow: early boot identifies a CPU by PVR, installs `cur_cpu_spec`, runs setup callbacks, then applies feature fixups based on selected CPU/MMU/firmware masks. Later code uses possible/always masks to optimize feature tests and alternatives.

State and persistence: `cur_cpu_spec` persists as the runtime CPU capability source. Feature masks determine emitted alternatives, userspace HWCAP, cache geometry, machine-check handling, and CPU hotplug restore behavior.

Dependencies and integration: includes UAPI CPU feature definitions and asm constants. It integrates with ELF aux vectors, module feature matching, feature-fixup sections, CPU setup declarations, machine-check handlers, debug/watchpoint limits, and jump-label feature checks.

Risks and test signals: feature mask mistakes can expose unsupported instructions, omit required errata workarounds, or patch wrong code paths. The `struct cpu_spec` size is consumed by assembly-generated offsets. Test signals include boot on each supported CPU family, HWCAP validation, module feature matching, machine-check recovery tests, `objdump`/mkdefs offset checks, and CPU hotplug/resume.
