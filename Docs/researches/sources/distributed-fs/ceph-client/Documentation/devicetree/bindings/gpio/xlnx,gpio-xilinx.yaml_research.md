<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xlnx,gpio-xilinx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xlnx,gpio-xilinx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xlnx,gpio-xilinx.yaml` defines the GPIO controller binding titled `Xilinx AXI GPIO controller`. Description from the schema: The AXI GPIO design provides a general purpose input/output interface to an AXI4-Lite interface. The AXI GPIO can be configured as either a single or a dual-channel device. The width of each channel is independently configurable. The channels can be configured to generate an interrupt when a transition on any of their inputs occurs. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `xlnx,xps-gpio-1.00.a`. Top-level properties are `compatible`, `reg`, `#gpio-cells`, `interrupts`, `gpio-controller`, `gpio-line-names`, `interrupt-controller`, `#interrupt-cells`, `clocks`, `interrupt-names`, `xlnx,all-inputs`, `xlnx,all-inputs-2`, `xlnx,all-outputs`, `xlnx,all-outputs-2`, `xlnx,dout-default`, `xlnx,dout-default-2`, `xlnx,gpio-width`, `xlnx,gpio2-width`, `xlnx,interrupt-present`, `xlnx,is-dual`, `xlnx,tri-default`, `xlnx,tri-default-2`. Required top-level properties are `reg`, `compatible`, `clocks`, `gpio-controller`, `#gpio-cells`. Pattern properties are none. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Neeli Srinivas <srinivas.neeli@amd.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/xlnx,gpio-xilinx.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/xlnx,gpio-xilinx.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xlnx,gpio-xilinx.yaml -->
