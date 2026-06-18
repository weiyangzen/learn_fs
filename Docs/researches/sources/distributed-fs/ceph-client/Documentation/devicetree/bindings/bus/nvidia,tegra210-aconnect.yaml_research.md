# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/nvidia,tegra210-aconnect.yaml

## Purpose
The Tegra ACONNECT bus is an AXI switch which is used to connect various components inside the Audio Processing Engine (APE). It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Jon Hunter <jonathanh@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra210-aconnect`, `nvidia,tegra264-aconnect`, `nvidia,tegra234-aconnect`, `nvidia,tegra186-aconnect`, `nvidia,tegra194-aconnect`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `clocks`, `clock-names`, `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, `power-domains` (items ?..1). Required properties are `compatible`, `clocks`, `clock-names`, `power-domains`, `#address-cells`, `#size-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/nvidia,tegra210-aconnect.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra210-aconnect`, `nvidia,tegra264-aconnect`, `nvidia,tegra234-aconnect`, `nvidia,tegra186-aconnect`, `nvidia,tegra194-aconnect`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
