# sources/distributed-fs/ceph-client/arch/x86/include/asm/perf_event.h

Purpose: defines the x86 perf hardware contract: Intel/AMD event-select bitfields, CPUID capability structures, fixed and topdown pseudo counter indexes, PEBS/architectural PEBS record layouts, AMD IBS controls, perf architecture hooks, guest PMU switching interfaces, and vendor virtualization helpers.

Important APIs, types, and functions: key constants cover `ARCH_PERFMON_EVENTSEL_*`, Intel fixed counter MSRs/indexes, TopDown metric encodings, global status bits, AMD64 event and L3 masks, IBS capability/control bits, and PEBS data configuration bits. Important types include CPUID unions for leaves 0x0a, 0x23, 0x1c, and 0x80000022, `struct x86_pmu_capability`, PEBS/arch-PEBS record structs, `struct x86_perf_regs`, `struct perf_guest_switch_msr`, and `struct x86_pmu_lbr`. Helper APIs include `use_fixed_pseudo_encoding()`, `is_metric_idx()`, `is_topdown_idx()`, `get_ibs_caps()`, `forward_event_to_ibs()`, `perf_events_lapic_init()`, architecture IP/misc flag hooks, `perf_arch_fetch_caller_regs`, PMU capability/config getters, microcode/dirty-counter hooks, RDPMC index lookup, guest LVTPC/MSR/LBR helpers, Intel PT VMX callback, AMD PMU virtualization, and optional low-power callback static call.

Control flow: this header does not drive PMU programming directly; it defines encodings and dispatch declarations consumed by Intel/AMD perf drivers, KVM, APIC setup, and generic perf. Compile-time vendor/config guards provide no-op fallbacks when perf or vendor support is absent.

State and persistence: data structures describe CPU MSR/PEBS state and sampled register payloads. Actual counters, LBRs, PEBS buffers, and IBS state are hardware/runtime state owned by perf drivers.

Dependencies and integration points: integrates with `linux/perf_event`, static calls, local APIC, KVM guest switching, Intel PT, AMD BRS, PEBS, IBS, RDPMC, and `copy_from_user_nmi` for perf output copying.

Risks: event encodings are user-visible ABI through perf raw events and sysfs. Record layouts must match hardware exactly. Pseudo-counter indexes overlap with overflow status bits by design and must remain coordinated with PMI handling. Guest PMU switching must preserve host counters and virtualization isolation.

Test signals: `perf list`, raw event programming on Intel/AMD, fixed counters, TopDown metrics, PEBS sampling with memory/GPR/XMM/LBR/counter payloads, IBS fetch/op sampling, KVM PMU passthrough/mediated modes, RDPMC index tests, microcode update handling, and low-power AMD BRS callbacks.
