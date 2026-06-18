<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml` defines the MMIO controller or bus binding titled `ARM Juno FPGA APB Registers`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells` with required set `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`. The `compatible` property uses ordered `items` sequence and lists 3 compatible tokens including `arm,juno-fpga-apb-regs`, `syscon`, `simple-mfd`. Pattern properties are `^led@[0-9a-f]+,[0-9a-f]$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Sudeep Holla <sudeep.holla@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/leds/register-bit-led.yaml#`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml -->
