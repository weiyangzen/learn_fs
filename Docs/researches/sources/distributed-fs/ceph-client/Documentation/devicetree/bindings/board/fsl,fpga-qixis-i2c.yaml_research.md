# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,fpga-qixis-i2c.yaml

## Purpose
Device-tree schema for Freescale on-board FPGA connected on I2C bus. It is a board-management binding used for board FPGA/CPLD or control-block discovery and child bus exposure. The binding is maintained by Frank Li <Frank.Li@nxp.com> and gives dt-schema a canonical contract for nodes matching `fsl,bsc9132qds-fpga`, `fsl,fpga-qixis-i2c`, `fsl,ls1028aqds-fpga`, `fsl,lx2160aqds-fpga`, `simple-mfd`, `fsl,lx2160ardb-fpga`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 0), `mux-controller` (ref reg-mux.yaml). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), 1 conditional `if` branch(es), child-node patterns `^gpio@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/mux/reg-mux.yaml. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=board/fsl,fpga-qixis-i2c.yaml`
- run `make dtbs_check` on DTS files using `fsl,bsc9132qds-fpga`, `fsl,fpga-qixis-i2c`, `fsl,ls1028aqds-fpga`, `fsl,lx2160aqds-fpga`, `simple-mfd`, `fsl,lx2160ardb-fpga`
- the 3 embedded example block(s) should compile through dtc and validate against referenced schemas
