# sources/distributed-fs/ceph-client/arch/x86/include/asm/perf_event_p4.h

Purpose: defines NetBurst/Pentium 4 perf event encodings, ESCR/CCCR bitfields, event masks, PEBS metrics, HyperThreading handling helpers, and packed configuration format used by the P4 PMU driver.

Important APIs, types, and functions: constants include `ARCH_P4_TOTAL_ESCR`, `ARCH_P4_MAX_ESCR`, `ARCH_P4_MAX_CCCR`, counter width masks, ESCR event/eventmask/tag/thread bits, CCCR overflow/PMI/cascade/edge/thread bits, raw config masks, alias masks, PEBS config bits, and PEBS enable bits. Helpers include `p4_config_pack/unpack_escr/cccr()`, `p4_config_unpack_emask/event/metric/pebs()`, `p4_config_pebs_has()`, `p4_is_event_cascaded()`, HT helpers `p4_ht_config_thread()`, `p4_set/clear_ht_bit()`, `p4_ht_active()`, `p4_ht_thread()`, `p4_should_swap_ts()`, `p4_default_cccr_conf()`, and `p4_default_escr_conf()`. Enums enumerate `P4_EVENTS`, opcode encodings, ESCR event masks, and `P4_PEBS_METRIC`.

Control flow: the P4 perf implementation packs ESCR in the high 32 bits and CCCR in the low 32 bits of `perf_event_attr.config`, uses opcode/event-mask enums to select hardware registers, and applies HT thread swaps based on logical CPU sibling position.

State and persistence: no state is owned. The packed config is carried in perf events and eventually programmed into P4 hardware MSRs.

Dependencies and integration points: depends on CPU sibling maps, `__max_threads_per_core`, bitops, and the NetBurst PMU implementation. It intersects with legacy PEBS and HT-shared MSR behavior.

Risks: NetBurst PMU register topology is irregular, shared across HT siblings, and contains reserved/dangerous bits. Aliasable events must preserve caller bits while hiding kernel-internal bits. Incorrect thread selection or ESCR restriction mapping gives wrong counts or wrong PMI routing.

Test signals: perf event programming on Pentium 4/old Xeon or emulator, HT on/off, raw event mask validation, cascaded events, PEBS metrics on allowed counters, event alias handling, and counter overflow PMI delivery to the correct logical thread.
