# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra186-pmc.yaml

## Purpose
Device-tree schema for NVIDIA Tegra Power Management Controller (PMC). It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra186-pmc`, `nvidia,tegra194-pmc`, `nvidia,tegra234-pmc`, `nvidia,tegra264-pmc`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum nvidia,tegra186-pmc, nvidia,tegra194-pmc, nvidia,tegra234-pmc, nvidia,tegra264-pmc), `reg` (items 3..5), `reg-names` (items 3..?), `interrupt-controller`, `#interrupt-cells` (const 2; Specifies the number of cells needed to encode an interrupt source.), `nvidia,invert-interrupt` (ref flag; If present, inverts the PMU interrupt signal.). Required properties are `compatible`, `reg`, `reg-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 3 `allOf` composition block(s), 4 conditional `if` branch(es), child-node patterns `^[a-z0-9]+-[a-z0-9]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/flag, /schemas/types.yaml#/definitions/string, /schemas/types.yaml#/definitions/uint32, example includes dt-bindings/clock/tegra186-clock.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/memory/tegra186-mc.h, dt-bindings/pinctrl/pinctrl-tegra-io-pad.h, plus 1 more. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tegra/nvidia,tegra186-pmc.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra186-pmc`, `nvidia,tegra194-pmc`, `nvidia,tegra234-pmc`, `nvidia,tegra264-pmc`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
