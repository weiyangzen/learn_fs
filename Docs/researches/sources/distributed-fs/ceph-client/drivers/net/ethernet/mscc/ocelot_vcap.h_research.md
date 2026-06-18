# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vcap.h

Purpose: private Ocelot VCAP header that exposes the local VCAP initialization, stats, and TC flower setup entry points used by the mscc Ethernet driver pieces. It bridges driver-private Ocelot types with the shared SoC VCAP definitions.

Important APIs/types: defines `OCELOT_POLICER_DISCARD` as `0x17f`, the reserved policer used by `ocelot_vcap_init` and ACL drop actions. Declares `ocelot_vcap_filter_stats_update`, `ocelot_vcap_init`, and `ocelot_setup_tc_cls_flower`.

Control flow: this file has no executable flow; it constrains call visibility and include ordering. Implementations live in `ocelot_vcap.c` and TC flower code elsewhere.

State and persistence: no direct state. The discard policer constant is a durable contract with the VCAP code and hardware policer range configured by the platform.

Dependencies and integration: includes driver-private `ocelot.h`, shared `<soc/mscc/ocelot_vcap.h>`, and `<net/flow_offload.h>`. It is consumed by Ocelot port/TC integration code that needs to initialize VCAP and translate flower classifiers.

Risks: changing the discard policer value without matching platform limits or QoS policer setup can break ACL drop semantics. Prototype drift would break VCAP/TC integration at compile time.

Test signals: build coverage for `CONFIG_MSCC_OCELOT_SWITCH` paths and runtime TC flower drop/stat rules that depend on `OCELOT_POLICER_DISCARD`.
