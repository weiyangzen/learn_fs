# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/qcom,ssbi.yaml

## Purpose
Some Qualcomm MSM devices contain a point-to-point serial bus used to communicate with a limited range of devices (mostly power management chips). It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Andy Gross <agross@kernel.org>, Bjorn Andersson <andersson@kernel.org> and gives dt-schema a canonical contract for nodes matching `qcom,ssbi`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const qcom,ssbi), `reg` (items ?..1), `qcom,controller-type` (enum ssbi, ssbi2, pmic-arbiter; Indicates the SSBI bus variant the controller should use to talk with the slave device.), `pmic` (ref qcom-pm8xxx.yaml#). Required properties are `compatible`, `reg`, `qcom,controller-type`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/mfd/qcom-pm8xxx.yaml#, example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/qcom,ssbi.yaml`
- run `make dtbs_check` on DTS files using `qcom,ssbi`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
