# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32mp131-dbg-bus.yaml

## Purpose
The STM32 debug bus is in charge of checking the debug configuration of the platform before probing the peripheral drivers that rely on the debug domain. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Gatien Chevallier <gatien.chevallier@foss.st.com> and gives dt-schema a canonical contract for nodes matching `st,stm32mp131-dbg-bus`, `st,stm32mp151-dbg-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `#address-cells` (const 1), `#size-cells` (const 1), `ranges` (items 1..2), `#access-controller-cells` (const 1; Contains the debug profile necessary to access the peripheral.). Required properties are `#access-controller-cells`, `#address-cells`, `#size-cells`, `compatible`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/stm32mp1-clks.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/st,stm32mp131-dbg-bus.yaml`
- run `make dtbs_check` on DTS files using `st,stm32mp131-dbg-bus`, `st,stm32mp151-dbg-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
