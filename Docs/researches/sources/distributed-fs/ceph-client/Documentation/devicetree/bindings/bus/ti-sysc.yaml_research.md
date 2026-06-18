# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/ti-sysc.yaml

## Purpose
Texas Instruments SoCs can have a generic interconnect target module for devices connected to various interconnects such as L3 interconnect using Arteris NoC, and L4 interconnect using Sonics s3220. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Tony Lindgren <tony@atomide.com> and gives dt-schema a canonical contract for nodes matching `ti,sysc-omap2`, `ti,sysc-omap4`, `ti,sysc-omap4-simple`, `ti,sysc-omap2-timer`, `ti,sysc-omap4-timer`, `ti,sysc-omap3430-sr`, `ti,sysc-omap3630-sr`, `ti,sysc-omap4-sr`, `ti,sysc-omap3-sham`, `ti,sysc-omap-aes`, plus 6 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items 1..3; Interconnect target module control registers consisting of REVISION, SYSCONFIG and SYSSTATUS registe), `reg-names` (Interconnect target module control register names consisting of "rev", "sysc" and "syss".), `clocks` (items 1..4; Target module clocks consisting of one functional clock, one interface clock, and up to 8 module spe), `clock-names` (Target module clock names like "fck", "ick", "optck1", "optck2" if the clocks are configurable.), `resets` (items ?..1; Target module reset bit in the RSTCTRL register if wired for the module.), `reset-names` (Target module reset names in the RSTCTRL register, typically named "rstctrl" if only one reset bit i), `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, plus 2 more. Required properties are `compatible`, `#address-cells`, `#size-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: {'type': 'object'}`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/string, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, example includes dt-bindings/bus/ti-sysc.h, dt-bindings/clock/omap4.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/ti-sysc.yaml`
- run `make dtbs_check` on DTS files using `ti,sysc-omap2`, `ti,sysc-omap4`, `ti,sysc-omap4-simple`, `ti,sysc-omap2-timer`, `ti,sysc-omap4-timer`, `ti,sysc-omap3430-sr`, `ti,sysc-omap3630-sr`, `ti,sysc-omap4-sr`, `ti,sysc-omap3-sham`, `ti,sysc-omap-aes`, plus 6 more
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
