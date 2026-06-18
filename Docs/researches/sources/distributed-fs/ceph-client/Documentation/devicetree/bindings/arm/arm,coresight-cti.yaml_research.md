<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml` defines the CoreSight trace/debug binding titled `ARM Coresight Cross Trigger Interface (CTI) device.`. The CoreSight Embedded Cross Trigger (ECT) consists of CTI devices connected to one or more CoreSight components and/or a CPU, with CTIs interconnected in a star topology via the Cross Trigger Matrix (CTM), which is not programmable. The ECT components are not part of the trace generation data path and are thus not part of the CoreSight graph. The CTI component properties define the connections between the individual CTI and the components it is directly connected to, consisting of input and output hardware trigger signals. CTIs can have a maximum number of input and output hardware trigger signals (8 each for v1 CTI, 32 each for v2 CTI). The number is defined at design time, the maximum... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses `oneOf` with 2 accepted compatible sequences for 3 compatible tokens and defines properties `$nodename`, `compatible`, `reg`, `cpu`, `power-domains`, `label`, `arm,cti-ctm-id`, `arm,cs-dev-assoc`, `#size-cells`, `#address-cells`, `access-controllers`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`; graph-related pattern properties are `^trig-conns@([0-9]+)$`.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mike Leach <mike.leach@linaro.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Top-level conditionals: `allOf`, `if`, `then`. Examples present: 4 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml -->
