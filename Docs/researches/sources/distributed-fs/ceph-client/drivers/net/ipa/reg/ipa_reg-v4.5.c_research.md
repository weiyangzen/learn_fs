# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.5.c

Purpose: Defines IPA core register descriptors for IPA v4.5 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_5`. The map covers expanded compatibility and clock fields, route/default pipe fields, shared memory and QSB limits, legacy hash flush, aggregation active/force-close, packet processor context, TX configuration, flavor, idle indication, Qtime timestamp, XO/timer pulse granularity, source/destination resource groups, endpoint configuration/status, combined endpoint filter/router hash config, and IRQ/UC/suspend blocks.

Control flow and integration: IPA v4.5 runtime code uses this table through `ipa_reg()` for endpoint bring-up, resource configuration, table hash flush, interrupt handling, and timestamp/timer setup.

State and persistence: Static descriptors only; hardware register values are persistent until reset or reprogramming.

Dependencies: Depends on `ipa_reg.h` enum IDs and `reg.h` helper semantics. Table code relies on the legacy `FILT_ROUT_HASH_FLUSH` and `ENDP_FILTER_ROUTER_HSH_CFG` descriptors present here.

Risks: v4.5 is a feature-rich pre-v5 map; using v5 cache descriptors would be wrong, but using older v4.2 assumptions would miss timer/qtime fields. Field-mask changes in `COMP_CFG` and endpoint aggregation can affect performance or correctness.

Test signals: Probe v4.5, configure timers and timestamps, initialize endpoints/resources, flush legacy hash tables, exercise IPA and UC interrupts, and validate traffic with aggregation/deaggregation settings.
