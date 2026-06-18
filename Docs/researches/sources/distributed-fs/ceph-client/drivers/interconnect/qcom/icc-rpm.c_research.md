# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm.c

Purpose: common legacy Qualcomm SMD RPM interconnect provider. It registers topology nodes, programs AP-owned QoS, aggregates active/sleep bandwidth, sends RPM master/slave votes, and scales bus clocks.

Important APIs/types/functions: exports `qnoc_probe()` and `qnoc_remove()`. Internal helpers cover QNOC/BIMC/NoC QoS, RPM bandwidth sends, pre-aggregation, bucket aggregation, rate calculation, bus aggregation, and provider `set`.

Control flow: probe waits for SMD RPM, reads match data, allocates provider/onecell state, maps optional regmap, enables clocks for QoS programming, creates nodes/links, applies AP-owned QoS, registers provider, and populates child NoCs. Votes convert node aggregates to RPM and clock-rate requests with cached rate suppression.

State and persistence: provider stores regmap, clocks, bus clock descriptors, cached bus rates, keepalive, and ignore-ENXIO. Nodes store per-state aggregates and node clock caches.

Dependencies/integration: SMD RPM helpers, regmap/MMIO, CCF clocks, OF child population, Qualcomm extended tags, interconnect core.

Risks and test signals: test RPM deferral, QoS with clocks enabled, rollback, child population cleanup, active/sleep tags, keepalive minimum, cache correctness, `ignore_enxio`, and unchecked link-create errors.
