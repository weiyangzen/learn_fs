<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml` defines the Texas Instruments SoC service binding titled `Wakeup M3 IPC device`. The TI AM33xx and AM43xx family of devices use a small Cortex M3 co-processor (commonly referred to as Wakeup M3 or CM3) to help with various low power tasks that cannot be controlled from the MPU, like suspend/resume and certain deep C-states for CPU Idle. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `ti,am3352-wkup-m3-ipc`, `ti,am4372-wkup-m3-ipc`. Top-level properties are `compatible`, `reg`, `interrupts`, `ti,rproc`, `mboxes`, `firmware-name`, `ti,vtt-gpio-pin`, `ti,set-io-isolation`. Required top-level properties are `compatible`, `reg`, `interrupts`, `ti,rproc`, `mboxes`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. The highest-risk contract area is firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including firmware-mediated device state, ring/queue allocation, remote-processor resources, power-domain state, and IPC state owned by TI subsystem drivers.

## Dependencies and Integration Points
Maintainers listed: Dave Gerlach <d-gerlach@ti.com>, Drew Fustini <dfustini@baylibre.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Integration points include TI K3/DaVinci/PRUSS platform drivers, TI-SCI firmware channels, DMA/ring acceleration, power-domain providers, wakeup firmware, and board DTS validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml` against boards that instantiate it. The schema has 2 embedded examples; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml -->
