<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml` defines the Texas Instruments SoC service binding titled `Texas Instruments AM654 Serdes Control Syscon`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 3 tokens: `ti,am654-serdes-ctrl`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `mux-controller`. Required top-level properties are `compatible`, `reg`, `mux-controller`. Nested or reusable constraints include referenced schemas: `/schemas/mux/reg-mux.yaml#`. The highest-risk contract area is firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including firmware-mediated device state, ring/queue allocation, remote-processor resources, power-domain state, and IPC state owned by TI subsystem drivers.

## Dependencies and Integration Points
Maintainers listed: Nishanth Menon <nm@ti.com>. Schema dependencies include `/schemas/mux/reg-mux.yaml#`. Integration points include TI K3/DaVinci/PRUSS platform drivers, TI-SCI firmware channels, DMA/ring acceleration, power-domain providers, wakeup firmware, and board DTS validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml -->
