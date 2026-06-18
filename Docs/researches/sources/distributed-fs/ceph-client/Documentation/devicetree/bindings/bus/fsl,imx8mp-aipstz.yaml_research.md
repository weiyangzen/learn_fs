# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,imx8mp-aipstz.yaml

## Purpose
The secure AIPS bridge (AIPSTZ) acts as a bridge for AHB masters issuing transactions to IP Slave peripherals. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Laurentiu Mihalcea <laurentiu.mihalcea@nxp.com> and gives dt-schema a canonical contract for nodes matching `fsl,imx8mp-aipstz`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const fsl,imx8mp-aipstz), `reg` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 1), `ranges`, `power-domains` (items ?..1), `#access-controller-cells` (const 3; First cell - consumer ID Second cell - consumer type (master or peripheral) Third cell - configurati). Required properties are `compatible`, `reg`, `power-domains`, `#address-cells`, `#size-cells`, `#access-controller-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@(0|[1-9a-f][0-9a-f]*)$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/flag, example includes dt-bindings/clock/imx8mp-clock.h, dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/fsl,imx8mp-aipstz.yaml`
- run `make dtbs_check` on DTS files using `fsl,imx8mp-aipstz`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
