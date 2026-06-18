# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v5.5.c

Purpose: Defines IPA core register descriptors for IPA v5.5 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v5_5`. It follows the v5 cache-oriented layout while moving several top-level offsets relative to v5.0. It defines flavor, compatibility, clocks, route, shared memory, QSB, aggregation, cache flush, local packet context, TX, idle/qtime/timer, resource groups, endpoint config/status, split filter/router cache config, IPA IRQ, UC IRQ, and suspend descriptors.

Control flow and integration: IPA v5.5 hardware data selects this map, and common code uses it for endpoint/resource setup, cache flushes, interrupt control, and timer/TX configuration.

State and persistence: Static descriptor metadata only. Programmed register state persists in IPA hardware.

Dependencies: Coupled to v5-capable `ipa_reg.h` field IDs and version-selection logic. Table logic relies on its `FILT_ROUT_CACHE_FLUSH`, `ENDP_FILTER_CACHE_CFG`, and `ENDP_ROUTER_CACHE_CFG` descriptors.

Risks: v5.5 is close to v5.0 but has top-level offset shifts and some mask differences, such as compatibility and qtime fields. Reusing v5.0 offsets can silently program the wrong register. Offset-zero fallback handling from `reg_offset()` must not obscure real offset-zero registers in the v5 family.

Test signals: Probe v5.5, validate flavor/pipe limits, configure endpoints/resources/timers, flush caches, verify split cache tuple zeroing, handle IPA/UC/suspend IRQs, and run data traffic.
