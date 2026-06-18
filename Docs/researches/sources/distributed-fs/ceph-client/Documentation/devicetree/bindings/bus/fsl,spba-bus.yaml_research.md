# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,spba-bus.yaml

## Purpose
A simple bus enabling access to shared peripherals. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Shawn Guo <shawnguo@kernel.org> and gives dt-schema a canonical contract for nodes matching `fsl,aips`, `fsl,emi`, `fsl,spba-bus`, `simple-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`. Required properties are `compatible`, `#address-cells`, `#size-cells`, `reg`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: {'type': 'object'}`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/fsl,spba-bus.yaml`
- run `make dtbs_check` on DTS files using `fsl,aips`, `fsl,emi`, `fsl,spba-bus`, `simple-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
