# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/airoha,en7523-scu.yaml

## Purpose
This node defines the System Control Unit of the EN7523 SoC, a collection of registers configuring many different aspects of the SoC. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Felix Fietkau <nbd@nbd.name>, John Crispin <nbd@nbd.name> and gives dt-schema a canonical contract for nodes matching `airoha,en7523-scu`, `airoha,en7581-scu`, `econet,en751221-scu`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items 1..?), `#clock-cells` (const 1; The first cell indicates the clock number, see [1] for available clocks.), `#reset-cells` (const 1; ID of the controller reset line). Required properties are `compatible`, `reg`, `#clock-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s), 2 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/en7523-clk.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/airoha,en7523-scu.yaml`
- run `make dtbs_check` on DTS files using `airoha,en7523-scu`, `airoha,en7581-scu`, `econet,en751221-scu`
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
