# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/ampere_cspmu.c

Purpose: Implements the Ampere vendor backend for ARM CoreSight Architecture PMUs, initially for AmpereOne MCU PMUs. It supplies Ampere-specific event names, format fields, PMU naming, filter programming, and validation for shared MCU filters.

Important APIs and types: Defines `struct ampere_cspmu_ctx`, AmpereOne MCU event/format attribute arrays, extractor helpers for `event`, `threshold`, `rank`, and `bank`, and backend callbacks `ampere_cspmu_get_event_attrs()`, `ampere_cspmu_get_format_attrs()`, `ampere_cspmu_get_name()`, `ampere_cspmu_set_cc_filter()`, `ampere_cspmu_set_ev_filter()`, `ampere_cspmu_validate_event()`, and `ampere_cspmu_init_ops()`. Registers via `arm_cspmu_impl_register()` with implementer ID `ARM_CSPMU_IMPL_ID_AMPERE`.

Control flow: Module init registers an implementer match. When the generic driver sees an Ampere PMIIDR, it calls `ampere_cspmu_init_ops()`, which allocates context, points to static AmpereOne event/format tables, allocates a unique `ampere_mcu_pmu_%d` name through an IDA, stores context in `cspmu->impl.ctx`, and overrides generic callbacks. Event start in the generic driver calls the backend filter hooks; regular events write threshold, rank, and bank to `PMAUXR0..2`, while cycle-counter filtering is a dummy because `PMCCFILTR` is RES0. Validation requires all events in the group and already active hardware events to use the same global filter tuple.

State and persistence: Static event tables are immutable. Runtime state is per-PMU devm context plus names allocated from `mcu_pmu_ida`; filter values persist in PMAUXR registers while events are active. There is no explicit IDA free path in the backend, so IDs are monotonically allocated for the module lifetime.

Dependencies and integration points: Depends on `arm_cspmu.h`, generic CoreSight PMU backend registration, MMIO writes, module infrastructure, and topology headers. Integrated entirely through `struct arm_cspmu_impl_ops`.

Risks: MCU PMU filters are global, so allowing mismatched threshold/rank/bank among concurrent events would produce misleading counts; this file explicitly prevents that. Event tables encode vendor hardware ABI and need vendor documentation alignment. PMCCFILTR writes are suppressed because the register is RES0; removing the override could cause unnecessary writes. The IDA allocation is not released on remove, which is acceptable for small module-lifetime IDs but worth noting for repeated bind/unbind tests.

Test signals: Build/load `ampere_cspmu`, confirm deferred generic PMU probes bind after backend registration, inspect `events` and `format` sysfs files, run multiple MCU events with matching filters, verify mismatched group/active filters fail, run `cycles`, and confirm PMAUXR writes through register tracing or hardware counter behavior.
