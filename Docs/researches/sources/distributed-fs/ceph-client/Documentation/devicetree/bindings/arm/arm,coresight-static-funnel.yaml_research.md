<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight Static Trace Bus Funnel`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The Coresight static funnel merges 2-8 trace sources into a single trace stream. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses single `const` for 1 compatible token and defines properties `compatible`, `power-domains`, `label`, `in-ports`, `out-ports`. Required properties are `compatible`, `in-ports`, `out-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml -->
