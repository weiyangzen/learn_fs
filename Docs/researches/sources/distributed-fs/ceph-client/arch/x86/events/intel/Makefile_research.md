# sources/distributed-fs/ceph-client/arch/x86/events/intel/Makefile

Purpose: defines Kbuild object selection for Intel x86 perf event support. It wires Intel core PMU support, BTS, PEBS/DS, LBR, model-specific support, Intel PT, uncore, and C-state PMUs into the kernel build according to configuration symbols.

Important APIs/types/functions: this file has no C functions or types. Its build targets are `obj-$(CONFIG_CPU_SUP_INTEL)`, `obj-$(CONFIG_PERF_EVENTS_INTEL_UNCORE)`, `intel-uncore-objs`, `obj-$(CONFIG_PERF_EVENTS_INTEL_CSTATE)`, and `intel-cstate-objs`.

Control flow: when `CONFIG_CPU_SUP_INTEL` is enabled, Kbuild compiles `core.o`, `bts.o`, `ds.o`, `knc.o`, `lbr.o`, `p4.o`, `p6.o`, and `pt.o` into the architecture perf events build. When `CONFIG_PERF_EVENTS_INTEL_UNCORE` is enabled, Kbuild builds a composite `intel-uncore.o` from `uncore.o`, `uncore_nhmex.o`, `uncore_snb.o`, `uncore_snbep.o`, and `uncore_discovery.o`. When `CONFIG_PERF_EVENTS_INTEL_CSTATE` is enabled, Kbuild builds `intel-cstate.o` from `cstate.o`.

State and persistence: no runtime state is stored here. Its only persistent effect is build graph composition at compile time.

Dependencies and integration points: depends on kernel Kconfig symbols for Intel CPU support, Intel uncore perf events, and Intel C-state perf events. It integrates the Intel files under `arch/x86/events/intel/` with the parent x86 perf events Makefile and determines which object files can provide symbols consumed by `events/core.c` and other vendor paths.

Risks: missing an object under `CONFIG_CPU_SUP_INTEL` can produce unresolved symbols or silently disable a PMU feature such as BTS, DS/PEBS, LBR, model-specific P4/P6/KNC behavior, or Intel PT. Incorrect composite object membership for uncore or cstate support can break module linkage or leave platform-specific uncore discovery unavailable.

Test signals: validate relevant config combinations with `CONFIG_CPU_SUP_INTEL=y`, `CONFIG_PERF_EVENTS_INTEL_UNCORE=y/m`, and `CONFIG_PERF_EVENTS_INTEL_CSTATE=y/m`; check that `intel-uncore.o` and `intel-cstate.o` link their member objects; and boot Intel systems to confirm expected PMUs such as `cpu`, `intel_bts`, `intel_pt`, uncore devices, and cstate devices are present when configured.
