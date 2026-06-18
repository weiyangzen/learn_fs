# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra194-cbb.yaml

## Purpose
The Control Backbone (CBB) is comprised of the physical path from an initiator to a target's register configuration space. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Sumit Gupta <sumitg@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra194-cbb-noc`, `nvidia,tegra194-aon-noc`, `nvidia,tegra194-bpmp-noc`, `nvidia,tegra194-rce-noc`, `nvidia,tegra194-sce-noc`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum nvidia,tegra194-cbb-noc, nvidia,tegra194-aon-noc, nvidia,tegra194-bpmp-noc, nvidia,tegra194-rce-noc...), `reg` (items ?..1), `interrupts` (CCPLEX receives secure or nonsecure interrupt depending on error type.), `nvidia,apbmisc` (ref phandle; Specifies the apbmisc node which need to be used for reading the ERD register.), `nvidia,axi2apb` (ref phandle; Specifies the node having all axi2apb bridges which need to be checked for any error logged in their). Required properties are `compatible`, `reg`, `interrupts`, `nvidia,apbmisc`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle, example includes dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tegra/nvidia,tegra194-cbb.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra194-cbb-noc`, `nvidia,tegra194-aon-noc`, `nvidia,tegra194-bpmp-noc`, `nvidia,tegra194-rce-noc`, `nvidia,tegra194-sce-noc`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
