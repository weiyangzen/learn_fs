# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/simple-pm-bus.yaml

## Purpose
A Simple Power-Managed Bus is a transparent bus that doesn't need a real driver, as it's typically initialized by the boot loader. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Geert Uytterhoeven <geert+renesas@glider.be> and gives dt-schema a canonical contract for nodes matching `simple-pm-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (Shall contain "simple-pm-bus" in addition to a optional bus-specific compatible strings defined in i), `clocks`, `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, `power-domains` (items 1..?). Required properties are `compatible`, `#address-cells`, `#size-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/qcom,gcc-msm8996.h, dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/simple-pm-bus.yaml`
- run `make dtbs_check` on DTS files using `simple-pm-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
