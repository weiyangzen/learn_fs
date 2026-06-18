# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/cznic,moxtet.yaml

## Purpose
Turris Mox module status and configuration bus (over SPI) The driver finds the devices connected to the bus by itself, but it may be needed to reference some of them from other parts of the device tree. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Marek Behn <kabel@kernel.org> and gives dt-schema a canonical contract for nodes matching `cznic,moxtet`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const cznic,moxtet), `reg` (items ?..1), `interrupts` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 0), `spi-cpol`, `spi-cpha`, `spi-max-frequency`, `interrupt-controller`, `#interrupt-cells` (const 1), plus 1 more. Required properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `spi-cpol`, `spi-cpha`, `interrupts`, `interrupt-controller`, `#interrupt-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: {'type': 'object', 'required': ['reg']}`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/cznic,moxtet.yaml`
- run `make dtbs_check` on DTS files using `cznic,moxtet`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
