# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v5.0.c

Purpose: Defines IPA core register descriptors for IPA v5.0 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v5_0`. The map moves many core offsets, starts with `FLAVOR_0`, uses v5-style route and shared-memory fields, replaces legacy hash flush with `FILT_ROUT_CACHE_FLUSH`, uses wider/newer resource limit masks, changes endpoint stride to `0x80`, and splits endpoint filter and router cache configuration into `ENDP_FILTER_CACHE_CFG` and `ENDP_ROUTER_CACHE_CFG`.

Control flow and integration: Selected for IPA v5.0 platforms. Table code writes unified filter/router cache flush bits and zeroes split cache config registers. Endpoint/resource/interrupt setup uses the v5 offsets and field masks through `ipa_reg()`.

State and persistence: Static descriptor state only; hardware register state persists outside this file.

Dependencies: Depends on common IPA register IDs and field IDs being broad enough to represent both pre-v5 hash and v5 cache layouts.

Risks: This is a major layout boundary. Pre-v5 code assumptions about filter bitmap shifting, combined hash tuple registers, and legacy hash flush are wrong for v5. Incorrect offset zero handling is important because `FLAVOR_0` is at offset 0.

Test signals: Probe v5.0, read flavor/max-pipe data, initialize endpoints with `0x80` stride, flush route/filter caches after table changes, verify split cache tuple zeroing, exercise interrupts and traffic.
