# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/qcom,ssc-block-bus.yaml

## Purpose
This binding describes the dependencies (clocks, resets, power domains) which need to be turned on in a sequence before communication over the AHB bus becomes possible. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Michael Srba <Michael.Srba@seznam.cz> and gives dt-schema a canonical contract for nodes matching `qcom,msm8998-ssc-block-bus`, `qcom,ssc-block-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg`, `reg-names`, `clocks` (items ?..6), `clock-names`, `resets`, `reset-names`, `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, plus 2 more. Required properties are `compatible`, `reg`, `reg-names`, `#address-cells`, `#size-cells`, `ranges`, `clocks`, `clock-names`, `power-domains`, `power-domain-names`, `resets`, `reset-names`, plus 1 more.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: {'type': 'object'}`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle-array, example includes dt-bindings/clock/qcom,gcc-msm8998.h, dt-bindings/clock/qcom,rpmcc.h, dt-bindings/power/qcom-rpmpd.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/qcom,ssc-block-bus.yaml`
- run `make dtbs_check` on DTS files using `qcom,msm8998-ssc-block-bus`, `qcom,ssc-block-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
