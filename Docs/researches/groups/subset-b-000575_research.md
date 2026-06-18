# Research Group subset-b-000575

This grouped report covers Linux devicetree binding YAML schemas for GPIO, GPU, hwinfo, hwlock, hwmon, PMBus, and I2C hardware under the Ceph client source tree. Each file section is delimited for deterministic splitting into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,twl4030-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,twl4030-gpio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,twl4030-gpio.yaml` defines the GPIO controller binding titled `TI TWL4030 GPIO controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `ti,twl4030-gpio`. Top-level properties are `compatible`, `#gpio-cells`, `gpio-controller`, `#interrupt-cells`, `interrupt-controller`, `ti,debounce`, `ti,mmc-cd`, `ti,pullups`, `ti,pulldowns`, `ti,use-leds`. Required top-level properties are none declared. Pattern properties are none. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Aaro Koskinen <aaro.koskinen@iki.fi>, Andreas Kemnade <andreas@kemnade.info>, Kevin Hilman <khilman@baylibre.com>, Roger Quadros <rogerq@kernel.org>, Tony Lindgren <tony@atomide.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/ti,twl4030-gpio.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/ti,twl4030-gpio.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,twl4030-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/toshiba,gpio-visconti.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/toshiba,gpio-visconti.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/toshiba,gpio-visconti.yaml` defines the GPIO controller binding titled `Toshiba Visconti ARM SoCs GPIO controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `toshiba,gpio-tmpv7708`. Top-level properties are `compatible`, `reg`, `#gpio-cells`, `gpio-ranges`, `gpio-controller`, `interrupt-controller`, `#interrupt-cells`, `interrupts`. Required top-level properties are `compatible`, `reg`, `#gpio-cells`, `gpio-ranges`, `gpio-controller`, `interrupt-controller`, `#interrupt-cells`. Pattern properties are none. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Nobuhiro Iwamatsu <nobuhiro1.iwamatsu@toshiba.co.jp>. Dependencies include dt-schema core/meta schemas only. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/toshiba,gpio-visconti.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/toshiba,gpio-visconti.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/toshiba,gpio-visconti.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/trivial-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/trivial-gpio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/trivial-gpio.yaml` defines the GPIO controller binding titled `Trivial 2-cell GPIO controllers`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. This file delegates most chip identity to `Documentation/devicetree/bindings/trivial-devices.yaml`; its local API is the shared GPIO-controller shape for simple I2C/SPI expander-like chips. Top-level properties are `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `gpio-line-names`, `ngpios`. Required top-level properties are `compatible`, `#gpio-cells`, `gpio-controller`. Pattern properties are `^(hog-[0-9]+|.+-hog(-[0-9]+)?)$`. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Bartosz Golaszewski <brgl@bgdev.pl>. Dependencies include dt-schema core/meta schemas only. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; pattern property regexes can over-match or under-match child nodes; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated; the split between this schema and `trivial-devices.yaml` can leave simple expanders incompletely described.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/trivial-gpio.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/trivial-gpio.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/trivial-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml` defines the GPIO controller binding titled `X-Powers AXP209 GPIO`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 6 tokens: `x-powers,axp209-gpio`, `x-powers,axp221-gpio`, `x-powers,axp813-gpio`, `x-powers,axp223-gpio`, `x-powers,axp809-gpio`, `x-powers,axp803-gpio`. Top-level properties are `#gpio-cells`, `compatible`, `gpio-controller`. Required top-level properties are `compatible`, `#gpio-cells`, `gpio-controller`. Pattern properties are `^.*-pins?$`. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>. Dependencies include `/schemas/pinctrl/pinmux-node.yaml#`. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xlnx,zynqmp-gpio-modepin.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xlnx,zynqmp-gpio-modepin.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xlnx,zynqmp-gpio-modepin.yaml` defines the GPIO controller binding titled `ZynqMP Mode Pin GPIO controller`. Description from the schema: PS_MODE is 4-bits boot mode pins sampled on POR deassertion. Mode Pin GPIO controller with configurable from numbers of pins (from 0 to 3 per PS_MODE). Every pin can be configured as input/output. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `xlnx,zynqmp-gpio-modepin`. Top-level properties are `compatible`, `gpio-controller`, `#gpio-cells`, `label`. Required top-level properties are `compatible`, `gpio-controller`, `#gpio-cells`. Pattern properties are none. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Radhey Shyam Pandey <radhey.shyam.pandey@amd.com>. Dependencies include dt-schema core/meta schemas only. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/xlnx,zynqmp-gpio-modepin.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/xlnx,zynqmp-gpio-modepin.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xlnx,zynqmp-gpio-modepin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xylon,logicvc-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xylon,logicvc-gpio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xylon,logicvc-gpio.yaml` defines the GPIO controller binding titled `Xylon LogiCVC GPIO controller`. Description from the schema: The LogiCVC GPIO describes the GPIO block included in the LogiCVC display controller. These are meant to be used for controlling display-related signals. The controller exposes GPIOs from the display and power control registers, which are mapped by the driver as follows: - GPIO[4:0] (display control) mapped to index 0-4 - EN_BLIGHT (power control) mapped to index 5 - EN_VDD (power control) mapped to index 6 - EN_V... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `xylon,logicvc-3.02.a-gpio`. Top-level properties are `$nodename`, `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `gpio-line-names`. Required top-level properties are `compatible`, `reg`, `#gpio-cells`, `gpio-controller`. Pattern properties are none. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Paul Kocialkowski <paul.kocialkowski@bootlin.com>. Dependencies include dt-schema core/meta schemas only. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/xylon,logicvc-gpio.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/xylon,logicvc-gpio.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/xylon,logicvc-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/apple,agx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/apple,agx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/apple,agx.yaml` defines the GPU or 2D accelerator binding titled `Apple SoC GPU`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 8 tokens: `apple,agx-g13g`, `apple,agx-g13s`, `apple,agx-g14g`, `apple,agx-g14s`, `apple,agx-g13c`, `apple,agx-g13d`, `apple,agx-g14c`, `apple,agx-g14d`. Top-level properties are `compatible`, `reg`, `reg-names`, `power-domains`, `mboxes`, `memory-region`, `memory-region-names`, `apple,firmware-abi`. Required top-level properties are `compatible`, `reg`, `mboxes`, `memory-region`, `apple,firmware-abi`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Sasha Finkelstein <k@chaosmail.tech>. Dependencies include `/schemas/types.yaml#/definitions/uint32-array`. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/apple,agx.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/apple,agx.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/apple,agx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml` defines the GPU or 2D accelerator binding titled `ARM Mali Bifrost GPU`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 23 tokens: `allwinner,sun50i-h616-mali`, `amlogic,meson-g12a-mali`, `mediatek,mt8183-mali`, `mediatek,mt8183b-mali`, `mediatek,mt8186-mali`, `mediatek,mt8365-mali`, `realtek,rtd1619-mali`, `renesas,r9a07g044-mali`, `renesas,r9a07g054-mali`, `renesas,r9a09g047-mali`, `renesas,r9a09g056-mali`, `renesas,r9a09g057-mali`, `rockchip,px30-mali`, `rockchip,rk3562-mali`, and 9 more. Top-level properties are `$nodename`, `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `mali-supply`, `sram-supply`, `operating-points-v2`, `power-domains`, `power-domain-names`, `resets`, `reset-names`, `#cooling-cells`, `dynamic-power-coefficient`, `dma-coherent`, `nvmem-cell-names`, `nvmem-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Rob Herring <robh@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-midgard.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-midgard.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-midgard.yaml` defines the GPU or 2D accelerator binding titled `ARM Mali Midgard GPU`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 10 branches with 21 tokens: `samsung,exynos5250-mali`, `arm,mali-t604`, `samsung,exynos5420-mali`, `arm,mali-t628`, `allwinner,sun50i-h6-mali`, `arm,mali-t720`, `amlogic,meson-gxm-mali`, `realtek,rtd1295-mali`, `arm,mali-t820`, `arm,juno-mali`, `arm,mali-t624`, `rockchip,rk3288-mali`, `samsung,exynos5433-mali`, `arm,mali-t760`, and 7 more. Top-level properties are `$nodename`, `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `mali-supply`, `opp-table`, `power-domains`, `resets`, `operating-points-v2`, `#cooling-cells`, `dma-coherent`, `dynamic-power-coefficient`. Required top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Rob Herring <robh@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-midgard.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-midgard.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-midgard.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-utgard.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-utgard.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-utgard.yaml` defines the GPU or 2D accelerator binding titled `ARM Mali Utgard GPU`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 26 tokens: `allwinner,sun8i-a23-mali`, `allwinner,sun7i-a20-mali`, `arm,mali-400`, `allwinner,sun4i-a10-mali`, `allwinner,sun8i-h3-mali`, `allwinner,sun8i-r40-mali`, `allwinner,sun50i-a64-mali`, `rockchip,rk3036-mali`, `rockchip,rk3066-mali`, `rockchip,rk3128-mali`, `rockchip,rk3188-mali`, `rockchip,rk3228-mali`, `samsung,exynos4210-mali`, `st,stih410-mali`, and 12 more. Top-level properties are `$nodename`, `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `memory-region`, `mali-supply`, `opp-table`, `power-domains`, `resets`, `operating-points-v2`, `#cooling-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Rob Herring <robh@kernel.org>, Maxime Ripard <mripard@kernel.org>, Heiko Stuebner <heiko@sntech.de>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-utgard.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-utgard.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-utgard.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-valhall-csf.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-valhall-csf.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-valhall-csf.yaml` defines the GPU or 2D accelerator binding titled `ARM Mali Valhall GPU`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 1 branch with 4 tokens: `mediatek,mt8196-mali`, `nxp,imx95-mali`, `rockchip,rk3588-mali`, `arm,mali-valhall-csf`. Top-level properties are `$nodename`, `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `nvmem-cells`, `nvmem-cell-names`, `mali-supply`, `operating-points-v2`, `opp-table`, `power-domains`, `power-domain-names`, `sram-supply`, `#cooling-cells`, `dynamic-power-coefficient`, `dma-coherent`. Required top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Liviu Dudau <liviu.dudau@arm.com>, Boris Brezillon <boris.brezillon@collabora.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-valhall-csf.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-valhall-csf.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-valhall-csf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/aspeed,ast2400-gfx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/aspeed,ast2400-gfx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/aspeed,ast2400-gfx.yaml` defines the GPU or 2D accelerator binding titled `ASPEED GFX Display Controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an ordered fallback `items` sequence with 4 tokens: `aspeed,ast2400-gfx`, `aspeed,ast2500-gfx`, `aspeed,ast2600-gfx`, `syscon`. Top-level properties are `compatible`, `reg`, `clocks`, `resets`, `interrupts`, `memory-region`, `syscon`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `memory-region`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Joel Stanley <joel@jms.id.au>. Dependencies include `/schemas/types.yaml#/definitions/phandle`. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/aspeed,ast2400-gfx.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/aspeed,ast2400-gfx.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/aspeed,ast2400-gfx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/brcm,bcm-v3d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/brcm,bcm-v3d.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/brcm,bcm-v3d.yaml` defines the GPU or 2D accelerator binding titled `Broadcom V3D GPU`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `brcm,2711-v3d`, `brcm,2712-v3d`, `brcm,7268-v3d`, `brcm,7278-v3d`. Top-level properties are `$nodename`, `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `resets`, `power-domains`. Required top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Maíra Canal <mcanal@igalia.com>, Nicolas Saenz Julienne <nsaenzjulienne@suse.de>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/brcm,bcm-v3d.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/brcm,bcm-v3d.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/brcm,bcm-v3d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml` defines the Tegra host1x media engine binding titled `NVIDIA Tegra NVDEC`. Description from the schema: NVDEC is the hardware video decoder present on NVIDIA Tegra210 and newer chips. It is located on the Host1x bus and typically programmed through Host1x channels. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `nvidia,tegra210-nvdec`, `nvidia,tegra186-nvdec`, `nvidia,tegra194-nvdec`. Top-level properties are `$nodename`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `iommus`, `dma-coherent`, `interconnects`, `interconnect-names`, `nvidia,host1x-class`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`. Pattern properties are none. The highest-risk API details are host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <treding@gmail.com>, Mikko Perttunen <mperttunen@nvidia.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the Tegra host1x bus, DRM/media engines, power domains, resets, clocks, IOMMU, and host1x channel clients. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvenc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvenc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvenc.yaml` defines the Tegra host1x media engine binding titled `NVIDIA Tegra NVENC`. Description from the schema: NVENC is the hardware video encoder present on NVIDIA Tegra210 and newer chips. It is located on the Host1x bus and typically programmed through Host1x channels. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `nvidia,tegra210-nvenc`, `nvidia,tegra186-nvenc`, `nvidia,tegra194-nvenc`. Top-level properties are `$nodename`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `iommus`, `dma-coherent`, `interconnects`, `interconnect-names`, `nvidia,host1x-class`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`. Pattern properties are none. The highest-risk API details are host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <treding@gmail.com>, Mikko Perttunen <mperttunen@nvidia.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the Tegra host1x bus, DRM/media engines, power domains, resets, clocks, IOMMU, and host1x channel clients. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvenc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvenc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvenc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvjpg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvjpg.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvjpg.yaml` defines the Tegra host1x media engine binding titled `NVIDIA Tegra NVJPG`. Description from the schema: NVJPG is the hardware JPEG decoder and encoder present on NVIDIA Tegra210 and newer chips. It is located on the Host1x bus and typically programmed through Host1x channels. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `nvidia,tegra210-nvjpg`, `nvidia,tegra186-nvjpg`, `nvidia,tegra194-nvjpg`. Top-level properties are `$nodename`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `iommus`, `dma-coherent`, `interconnects`, `interconnect-names`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`. Pattern properties are none. The highest-risk API details are host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <treding@gmail.com>, Mikko Perttunen <mperttunen@nvidia.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the Tegra host1x bus, DRM/media engines, power domains, resets, clocks, IOMMU, and host1x channel clients. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvjpg.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvjpg.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvjpg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra234-nvdec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra234-nvdec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra234-nvdec.yaml` defines the Tegra host1x media engine binding titled `NVIDIA Tegra234 NVDEC`. Description from the schema: NVDEC is the hardware video decoder present on NVIDIA Tegra210 and newer chips. It is located on the Host1x bus and typically programmed through Host1x channels. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `nvidia,tegra234-nvdec`. Top-level properties are `$nodename`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `iommus`, `dma-coherent`, `interconnects`, `interconnect-names`, `nvidia,memory-controller`, `nvidia,bl-manifest-offset`, `nvidia,bl-code-offset`, `nvidia,bl-data-offset`, `nvidia,os-manifest-offset`, `nvidia,os-code-offset`, `nvidia,os-data-offset`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `nvidia,memory-controller`, `nvidia,bl-manifest-offset`, `nvidia,bl-code-offset`, `nvidia,bl-data-offset`, `nvidia,os-manifest-offset`, `nvidia,os-code-offset`, `nvidia,os-data-offset`. Pattern properties are none. The highest-risk API details are host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <treding@gmail.com>, Mikko Perttunen <mperttunen@nvidia.com>. Dependencies include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the Tegra host1x bus, DRM/media engines, power domains, resets, clocks, IOMMU, and host1x channel clients. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra234-nvdec.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra234-nvdec.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra234-nvdec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/img,powervr-rogue.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/img,powervr-rogue.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/img,powervr-rogue.yaml` defines the GPU or 2D accelerator binding titled `Imagination Technologies PowerVR and IMG Rogue GPUs`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 6 branches with 15 tokens: `renesas,r8a7796-gpu`, `renesas,r8a77961-gpu`, `img,img-gx6250`, `img,img-rogue`, `renesas,r8a77965-gpu`, `renesas,r8a779a0-gpu`, `img,img-ge7800`, `ti,am62-gpu`, `img,img-axe-1-16m`, `img,img-axe`, `thead,th1520-gpu`, `img,img-bxm-4-64`, `ti,am62p-gpu`, `ti,j721s2-gpu`, and 1 more. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `power-domains`, `power-domain-names`, `dma-coherent`, `resets`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Frank Binns <frank.binns@imgtec.com>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/img,powervr-rogue.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/img,powervr-rogue.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/img,powervr-rogue.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/img,powervr-sgx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/img,powervr-sgx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/img,powervr-sgx.yaml` defines the GPU or 2D accelerator binding titled `Imagination Technologies PowerVR SGX GPUs`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 12 tokens: `ti,omap3430-gpu`, `ti,omap3630-gpu`, `img,powervr-sgx530`, `ingenic,jz4780-gpu`, `ti,omap4430-gpu`, `img,powervr-sgx540`, `allwinner,sun6i-a31-gpu`, `ti,omap4470-gpu`, `ti,omap5432-gpu`, `ti,am5728-gpu`, `ti,am6548-gpu`, `img,powervr-sgx544`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. Required top-level properties are `compatible`, `reg`, `interrupts`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Frank Binns <frank.binns@imgtec.com>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/img,powervr-sgx.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/img,powervr-sgx.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/img,powervr-sgx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/nvidia,gk20a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/nvidia,gk20a.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/nvidia,gk20a.yaml` defines the GPU or 2D accelerator binding titled `NVIDIA Tegra Graphics Processing Units`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `nvidia,gk20a`, `nvidia,gm20b`, `nvidia,gp10b`, `nvidia,gv11b`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `vdd-supply`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `interconnects`, `interconnect-names`, `iommus`, `dma-coherent`. Required top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Alexandre Courbot <acourbot@nvidia.com>, Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <treding@nvidia.com>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/nvidia,gk20a.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/nvidia,gk20a.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/nvidia,gk20a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-g2d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-g2d.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-g2d.yaml` defines the GPU or 2D accelerator binding titled `Samsung SoC 2D Graphics Accelerator`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `samsung,s5pv210-g2d`, `samsung,exynos4212-g2d`, `samsung,exynos5250-g2d`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `iommus`, `power-domains`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Inki Dae <inki.dae@samsung.com>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/samsung-g2d.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/samsung-g2d.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-g2d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-rotator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-rotator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-rotator.yaml` defines the GPU or 2D accelerator binding titled `Samsung SoC Image Rotator`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `samsung,s5pv210-rotator`, `samsung,exynos4210-rotator`, `samsung,exynos4212-rotator`, `samsung,exynos5250-rotator`. Top-level properties are `compatible`, `reg`, `interrupts`, `iommus`, `power-domains`, `clocks`, `clock-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Inki Dae <inki.dae@samsung.com>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/samsung-rotator.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/samsung-rotator.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-rotator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-scaler.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-scaler.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-scaler.yaml` defines the GPU or 2D accelerator binding titled `Samsung Exynos SoC Image Scaler`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `samsung,exynos5420-scaler`, `samsung,exynos5433-scaler`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `iommus`, `power-domains`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Inki Dae <inki.dae@samsung.com>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/samsung-scaler.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/samsung-scaler.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/samsung-scaler.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/vivante,gc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/vivante,gc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/vivante,gc.yaml` defines the GPU or 2D accelerator binding titled `Vivante GPU`. Description from the schema: Vivante GPU core devices It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `vivante,gc`. Top-level properties are `compatible`, `reg`, `interrupts`, `#cooling-cells`, `assigned-clock-parents`, `assigned-clock-rates`, `assigned-clocks`, `clocks`, `clock-names`, `resets`, `power-domains`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Lucas Stach <l.stach@pengutronix.de>. Dependencies include dt-schema core/meta schemas only. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/vivante,gc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/vivante,gc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/vivante,gc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/loongson,ls2k-chipid.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/loongson,ls2k-chipid.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/loongson,ls2k-chipid.yaml` defines the hardware-identification binding titled `Loongson-2 SoC ChipID`. Description from the schema: Loongson-2 SoC contains many groups of global utilities register blocks, of which the ChipID group registers record SoC version, feature, vendor and id information. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `loongson,ls2k-chipid`. Top-level properties are `compatible`, `reg`, `little-endian`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including read-only SoC ID or revision state exposed to platform code, sysfs/debugfs, or quirk selection paths.

## Dependencies and Integration Points
Maintainers listed: Yinbo Zhu <zhuyinbo@loongson.cn>. Dependencies include dt-schema core/meta schemas only. Integration points include SoC identification drivers, NVMEM/syscon/register readers, debugfs/sysfs exposure, and platform code that selects quirks by chip revision. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/loongson,ls2k-chipid.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/loongson,ls2k-chipid.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/loongson,ls2k-chipid.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/renesas,prr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/renesas,prr.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/renesas,prr.yaml` defines the hardware-identification binding titled `Renesas Product Register`. Description from the schema: Most Renesas ARM SoCs have a Product Register or Boundary Scan ID Register that allows to retrieve SoC product and revision information. If present, a device node for this register should be added. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `renesas,prr`, `renesas,bsid`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including read-only SoC ID or revision state exposed to platform code, sysfs/debugfs, or quirk selection paths.

## Dependencies and Integration Points
Maintainers listed: Geert Uytterhoeven <geert+renesas@glider.be>, Magnus Damm <magnus.damm@gmail.com>. Dependencies include dt-schema core/meta schemas only. Integration points include SoC identification drivers, NVMEM/syscon/register readers, debugfs/sysfs exposure, and platform code that selects quirks by chip revision. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/renesas,prr.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/renesas,prr.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/renesas,prr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/samsung,exynos-chipid.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/samsung,exynos-chipid.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/samsung,exynos-chipid.yaml` defines the hardware-identification binding titled `Samsung Exynos SoC series Chipid driver`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 14 tokens: `samsung,exynos4210-chipid`, `samsung,exynos850-chipid`, `samsung,exynos5433-chipid`, `samsung,exynos7-chipid`, `samsung,exynos7870-chipid`, `samsung,exynos8890-chipid`, `samsung,exynos2200-chipid`, `samsung,exynos7885-chipid`, `samsung,exynos8895-chipid`, `samsung,exynos9610-chipid`, `samsung,exynos9810-chipid`, `samsung,exynos990-chipid`, `samsung,exynosautov9-chipid`, `samsung,exynosautov920-chipid`. Top-level properties are `compatible`, `reg`, `samsung,asv-bin`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including read-only SoC ID or revision state exposed to platform code, sysfs/debugfs, or quirk selection paths.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include SoC identification drivers, NVMEM/syscon/register readers, debugfs/sysfs exposure, and platform code that selects quirks by chip revision. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/samsung,exynos-chipid.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/samsung,exynos-chipid.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/samsung,exynos-chipid.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/samsung,s5pv210-chipid.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/samsung,s5pv210-chipid.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/samsung,s5pv210-chipid.yaml` defines the hardware-identification binding titled `Samsung S5PV210 SoC ChipID`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `samsung,s5pv210-chipid`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including read-only SoC ID or revision state exposed to platform code, sysfs/debugfs, or quirk selection paths.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include SoC identification drivers, NVMEM/syscon/register readers, debugfs/sysfs exposure, and platform code that selects quirks by chip revision. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/samsung,s5pv210-chipid.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/samsung,s5pv210-chipid.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/samsung,s5pv210-chipid.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml` defines the hardware-identification binding titled `Texas Instruments K3 Multicore SoC platforms chipid module`. Description from the schema: Texas Instruments (ARM64) K3 Multicore SoC platforms chipid module is represented by CTRLMMR_xxx_JTAGID register which contains information about SoC id and revision. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `ti,am654-chipid`. Top-level properties are `$nodename`, `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including read-only SoC ID or revision state exposed to platform code, sysfs/debugfs, or quirk selection paths.

## Dependencies and Integration Points
Maintainers listed: Tero Kristo <t-kristo@ti.com>, Nishanth Menon <nm@ti.com>. Dependencies include dt-schema core/meta schemas only. Integration points include SoC identification drivers, NVMEM/syscon/register readers, debugfs/sysfs exposure, and platform code that selects quirks by chip revision. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/via,vt8500-scc-id.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/via,vt8500-scc-id.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/via,vt8500-scc-id.yaml` defines the hardware-identification binding titled `VIA/WonderMedia SoC system configuration information`. Description from the schema: The system configuration controller on VIA/WonderMedia SoC's contains a chip identifier and revision used to differentiate between different hardware versions of on-chip IP blocks having their own peculiarities which may or may not be captured by their respective DT compatible strings It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `via,vt8500-scc-id`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including read-only SoC ID or revision state exposed to platform code, sysfs/debugfs, or quirk selection paths.

## Dependencies and Integration Points
Maintainers listed: Alexey Charkov <alchark@gmail.com>. Dependencies include dt-schema core/meta schemas only. Integration points include SoC identification drivers, NVMEM/syscon/register readers, debugfs/sysfs exposure, and platform code that selects quirks by chip revision. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/via,vt8500-scc-id.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/via,vt8500-scc-id.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/via,vt8500-scc-id.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/allwinner,sun6i-a31-hwspinlock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/allwinner,sun6i-a31-hwspinlock.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/allwinner,sun6i-a31-hwspinlock.yaml` defines the hardware spinlock controller binding titled `SUN6I hardware spinlock driver for Allwinner sun6i compatible SoCs`. Description from the schema: The hardware unit provides semaphores between the ARM cores and the embedded companion core on the SoC. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `allwinner,sun6i-a31-hwspinlock`. Top-level properties are `compatible`, `reg`, `clocks`, `resets`, `#hwlock-cells`. Required top-level properties are `compatible`, `reg`, `clocks`, `resets`, `#hwlock-cells`. Pattern properties are none. The highest-risk API details are `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including lock-bank registration, remote-processor lock ownership, and hardware lock acquisition/release state.

## Dependencies and Integration Points
Maintainers listed: Wilken Gottwalt <wilken.gottwalt@posteo.net>. Dependencies include dt-schema core/meta schemas only. Integration points include the Linux hwspinlock framework, remoteproc/IPC users, syscon/regmap access, interrupts where present, and SoC DTS lock-bank nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/allwinner,sun6i-a31-hwspinlock.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/allwinner,sun6i-a31-hwspinlock.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/allwinner,sun6i-a31-hwspinlock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml` defines the hardware spinlock controller binding titled `Qualcomm Hardware Mutex Block`. Description from the schema: The hardware block provides mutexes utilized between different processors on the SoC as part of the communication protocol used by these processors. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 8 tokens: `qcom,sfpb-mutex`, `qcom,tcsr-mutex`, `qcom,apq8084-tcsr-mutex`, `qcom,ipq6018-tcsr-mutex`, `qcom,msm8226-tcsr-mutex`, `qcom,msm8994-tcsr-mutex`, `qcom,msm8974-tcsr-mutex`, `syscon`. Top-level properties are `compatible`, `reg`, `#hwlock-cells`. Required top-level properties are `compatible`, `reg`, `#hwlock-cells`. Pattern properties are none. The highest-risk API details are `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including lock-bank registration, remote-processor lock ownership, and hardware lock acquisition/release state.

## Dependencies and Integration Points
Maintainers listed: Bjorn Andersson <bjorn.andersson@linaro.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the Linux hwspinlock framework, remoteproc/IPC users, syscon/regmap access, interrupts where present, and SoC DTS lock-bank nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/sprd,hwspinlock-r3p0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/sprd,hwspinlock-r3p0.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/sprd,hwspinlock-r3p0.yaml` defines the hardware spinlock controller binding titled `Spreadtrum hardware spinlock`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `sprd,hwspinlock-r3p0`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#hwlock-cells`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#hwlock-cells`. Pattern properties are none. The highest-risk API details are `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including lock-bank registration, remote-processor lock ownership, and hardware lock acquisition/release state.

## Dependencies and Integration Points
Maintainers listed: Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the Linux hwspinlock framework, remoteproc/IPC users, syscon/regmap access, interrupts where present, and SoC DTS lock-bank nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/sprd,hwspinlock-r3p0.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/sprd,hwspinlock-r3p0.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/sprd,hwspinlock-r3p0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/st,stm32-hwspinlock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/st,stm32-hwspinlock.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/st,stm32-hwspinlock.yaml` defines the hardware spinlock controller binding titled `STMicroelectronics STM32 Hardware Spinlock`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `st,stm32-hwspinlock`. Top-level properties are `#hwlock-cells`, `compatible`, `reg`, `clocks`, `clock-names`. Required top-level properties are `#hwlock-cells`, `compatible`, `reg`, `clocks`, `clock-names`. Pattern properties are none. The highest-risk API details are `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including lock-bank registration, remote-processor lock ownership, and hardware lock acquisition/release state.

## Dependencies and Integration Points
Maintainers listed: Fabien Dessenne <fabien.dessenne@foss.st.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the Linux hwspinlock framework, remoteproc/IPC users, syscon/regmap access, interrupts where present, and SoC DTS lock-bank nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/st,stm32-hwspinlock.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/st,stm32-hwspinlock.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/st,stm32-hwspinlock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/ti,omap-hwspinlock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/ti,omap-hwspinlock.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/ti,omap-hwspinlock.yaml` defines the hardware spinlock controller binding titled `TI HwSpinlock for OMAP and K3 based SoCs`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `ti,omap4-hwspinlock`, `ti,am64-hwspinlock`, `ti,am654-hwspinlock`. Top-level properties are `compatible`, `reg`, `#hwlock-cells`. Required top-level properties are `compatible`, `reg`, `#hwlock-cells`. Pattern properties are none. The highest-risk API details are `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including lock-bank registration, remote-processor lock ownership, and hardware lock acquisition/release state.

## Dependencies and Integration Points
Maintainers listed: Suman Anna <s-anna@ti.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the Linux hwspinlock framework, remoteproc/IPC users, syscon/regmap access, interrupts where present, and SoC DTS lock-bank nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/ti,omap-hwspinlock.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/ti,omap-hwspinlock.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/ti,omap-hwspinlock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ad741x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ad741x.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ad741x.yaml` defines the hardware-monitor binding titled `Analog Devices AD7416/AD7417/AD7418 temperature sensors`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `adi,ad7416`, `adi,ad7417`, `adi,ad7418`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ad741x.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ad741x.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ad741x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1177.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1177.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1177.yaml` defines the hardware-monitor binding titled `Analog Devices ADM1177 Hot Swap Controller and Digital Power Monitor`. Description from the schema: Analog Devices ADM1177 Hot Swap Controller and Digital Power Monitor https://www.analog.com/media/en/technical-documentation/data-sheets/ADM1177.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,adm1177`. Top-level properties are `compatible`, `reg`, `avcc-supply`, `shunt-resistor-micro-ohms`, `adi,shutdown-threshold-microamp`, `adi,vrange-high-enable`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Michael Hennerich <michael.hennerich@analog.com>. Dependencies include `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,adm1177.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,adm1177.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1177.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1266.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1266.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1266.yaml` defines the hardware-monitor binding titled `Analog Devices ADM1266 Cascadable Super Sequencer with Margin Control and Fault Recording`. Description from the schema: Analog Devices ADM1266 Cascadable Super Sequencer with Margin Control and Fault Recording. https://www.analog.com/media/en/technical-documentation/data-sheets/ADM1266.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,adm1266`. Top-level properties are `compatible`, `reg`, `avcc-supply`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Cedric Encarnacion <cedricjustine.encarnacion@analog.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,adm1266.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,adm1266.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1266.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml` defines the hardware-monitor binding titled `Analog Devices ADM1075/ADM127x/ADM1281/ADM129x digital power monitors`. Description from the schema: The ADM1293 and ADM1294 are high accuracy integrated digital power monitors that offer digital current, voltage, and power monitoring using an on-chip, 12-bit analog-to-digital converter (ADC), communicated through a PMBus compliant I2C interface. Datasheets: https://www.analog.com/en/products/adm1294.html The SQ24905C is also a Hot-swap controller compatibility to the ADM1278, the PMBUS_MFR_MODEL is MC09C Datashe... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 10 tokens: `adi,adm1075`, `adi,adm1272`, `adi,adm1273`, `adi,adm1275`, `adi,adm1276`, `adi,adm1278`, `adi,adm1281`, `adi,adm1293`, `adi,adm1294`, `silergy,mc09c`. Top-level properties are `compatible`, `reg`, `adi,volt-curr-sample-average`, `adi,power-sample-average`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/uint32`, `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,axi-fan-control.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,axi-fan-control.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,axi-fan-control.yaml` defines the hardware-monitor binding titled `Analog Devices AXI FAN Control`. Description from the schema: Bindings for the Analog Devices AXI FAN Control driver. Specifications of the core can be found in: https://wiki.analog.com/resources/fpga/docs/axi_fan_control It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,axi-fan-control-1.00.a`. Top-level properties are `compatible`, `reg`, `clocks`, `interrupts`, `pulses-per-revolution`. Required top-level properties are `compatible`, `reg`, `clocks`, `interrupts`, `pulses-per-revolution`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Nuno Sá <nuno.sa@analog.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,axi-fan-control.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,axi-fan-control.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,axi-fan-control.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2945.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2945.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2945.yaml` defines the hardware-monitor binding titled `Analog Devices LTC2945 wide range i2c power monitor`. Description from the schema: Analog Devices LTC2945 wide range i2c power monitor over I2C. https://www.analog.com/media/en/technical-documentation/data-sheets/LTC2945.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,ltc2945`. Top-level properties are `compatible`, `reg`, `shunt-resistor-micro-ohms`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Guenter Roeck <linux@roeck-us.net>. Dependencies include `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc2945.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc2945.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2945.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2947.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2947.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2947.yaml` defines the hardware-monitor binding titled `Analog Devices LTC2947 high precision power and energy monitor`. Description from the schema: Analog Devices LTC2947 high precision power and energy monitor over SPI or I2C. https://www.analog.com/media/en/technical-documentation/data-sheets/LTC2947.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,ltc2947`. Top-level properties are `compatible`, `reg`, `clocks`, `adi,accumulator-ctl-pol`, `adi,accumulation-deadband-microamp`, `adi,gpio-out-pol`, `adi,gpio-in-accum`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Nuno Sá <nuno.sa@analog.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc2947.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc2947.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2947.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2991.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2991.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2991.yaml` defines the hardware-monitor binding titled `Analog Devices LTC2991 Octal I2C Voltage, Current and Temperature Monitor`. Description from the schema: The LTC2991 is used to monitor system temperatures, voltages and currents. Through the I2C serial interface, the eight monitors can individually measure supply voltages and can be paired for differential measurements of current sense resistors or temperature sensing transistors. Datasheet: https://www.analog.com/en/products/ltc2991.html It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `adi,ltc2991`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `vcc-supply`. Required top-level properties are `compatible`, `reg`, `vcc-supply`. Pattern properties are `^channel@[0-3]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Antoniu Miclaus <antoniu.miclaus@analog.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc2991.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc2991.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2991.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2992.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2992.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2992.yaml` defines the hardware-monitor binding titled `Linear Technology 2992 Power Monitor`. Description from the schema: Linear Technology 2992 Dual Wide Range Power Monitor https://www.analog.com/media/en/technical-documentation/data-sheets/ltc2992.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,ltc2992`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `avcc-supply`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^channel@([0-1])$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Cedric Encarnacion <cedricjustine.encarnacion@analog.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc2992.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc2992.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc2992.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml` defines the hardware-monitor binding titled `Analog Devices LTC4282 I2C High Current Hot Swap Controller over I2C`. Description from the schema: Analog Devices LTC4282 I2C High Current Hot Swap Controller over I2C. https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4282.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,ltc4282`. Top-level properties are `compatible`, `reg`, `vdd-supply`, `clocks`, `#clock-cells`, `adi,rsense-nano-ohms`, `adi,vin-mode-microvolt`, `adi,fet-bad-timeout-ms`, `adi,overvoltage-dividers`, `adi,undervoltage-dividers`, `adi,current-limit-sense-microvolt`, `adi,overcurrent-retry`, `adi,overvoltage-retry-disable`, `adi,undervoltage-retry-disable`, `adi,fault-log-enable`, `adi,gpio1-mode`, `adi,gpio2-mode`, `adi,gpio3-monitor-enable`. Required top-level properties are `compatible`, `reg`, `adi,rsense-nano-ohms`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Nuno Sa <nuno.sa@analog.com>. Dependencies include `/schemas/types.yaml#/definitions/string`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,max31760.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,max31760.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,max31760.yaml` defines the hardware-monitor binding titled `Analog Devices MAX31760 Fan-Speed Controller`. Description from the schema: Analog Devices MAX31760 Fan-Speed Controller https://datasheets.maximintegrated.com/en/ds/MAX31760.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,max31760`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Ibrahim Tilki <Ibrahim.Tilki@analog.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,max31760.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,max31760.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,max31760.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,max31827.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,max31827.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,max31827.yaml` defines the hardware-monitor binding titled `Analog Devices MAX31827, MAX31828, MAX31829 Low-Power Temperature Switch`. Description from the schema: Analog Devices MAX31827, MAX31828, MAX31829 Low-Power Temperature Switch with I2C Interface https://www.analog.com/media/en/technical-documentation/data-sheets/MAX31827-MAX31829.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 3 tokens: `adi,max31827`, `adi,max31828`, `adi,max31829`. Top-level properties are `compatible`, `reg`, `vref-supply`, `adi,comp-int`, `adi,alarm-pol`, `adi,fault-q`, `adi,timeout-enable`. Required top-level properties are `compatible`, `reg`, `vref-supply`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Daniel Matyas <daniel.matyas@analog.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,max31827.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,max31827.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,max31827.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adt7475.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adt7475.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adt7475.yaml` defines the hardware-monitor binding titled `ADT7475 hwmon sensor`. Description from the schema: The ADT7473, ADT7475, ADT7476, and ADT7490 are thermal monitors and multiple PWN fan controllers. They support monitoring and controlling up to four fans (the ADT7490 can only control up to three). They support reading a single on chip temperature sensor and two off chip temperature sensors (the ADT7490 additionally supports measuring up to three current external temperature sensors with series resistance cancella... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `adi,adt7473`, `adi,adt7475`, `adi,adt7476`, `adi,adt7490`. Top-level properties are `compatible`, `reg`, `adi,pwm-active-state`, `#pwm-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^adi,bypass-attenuator-in[0-4]$`, `^adi,pin(5|10)-function$`, `^adi,pin(9|14)-function$`, `^fan-[0-9]+$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jean Delvare <jdelvare@suse.com>. Dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `fan-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adt7475.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adt7475.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adt7475.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amd,sbrmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amd,sbrmi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amd,sbrmi.yaml` defines the hardware-monitor binding titled `Sideband Remote Management Interface (SB-RMI) compliant AMD SoC power device.
`. Description from the schema: SB Remote Management Interface (SB-RMI) is an SMBus compatible interface that reports AMD SoC's Power (normalized Power) using, Mailbox Service Request and resembles a typical 8-pin remote power sensor's I2C interface to BMC. The power attributes in hwmon reports power in microwatts. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `amd,sbrmi`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Akshay Gupta <Akshay.Gupta@amd.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/amd,sbrmi.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/amd,sbrmi.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amd,sbrmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amd,sbtsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amd,sbtsi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amd,sbtsi.yaml` defines the hardware-monitor binding titled `Sideband interface Temperature Sensor Interface (SB-TSI) compliant AMD SoC temperature device
`. Description from the schema: SB Temperature Sensor Interface (SB-TSI) is an SMBus compatible interface that reports AMD SoC's Ttcl (normalized temperature), and resembles a typical 8-pin remote temperature sensor's I2C interface to BMC. The emulated thermal sensor can report temperatures in increments of 0.125 degrees, ranging from 0 to 255.875. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `amd,sbtsi`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Kun Yi <kunyi@google.com>, Supreeth Venkatesh <supreeth.venkatesh@amd.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/amd,sbtsi.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/amd,sbtsi.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amd,sbtsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amphenol,chipcap2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amphenol,chipcap2.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amphenol,chipcap2.yaml` defines the hardware-monitor binding titled `ChipCap 2 humidity and temperature iio sensor`. Description from the schema: Relative humidity and temperature sensor on I2C bus. Datasheets: https://www.amphenol-sensors.com/en/telaire/humidity/527-humidity-sensors/3095-chipcap-2 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 8 tokens: `amphenol,cc2d23`, `amphenol,cc2d23s`, `amphenol,cc2d25`, `amphenol,cc2d25s`, `amphenol,cc2d33`, `amphenol,cc2d33s`, `amphenol,cc2d35`, `amphenol,cc2d35s`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `vdd-supply`. Required top-level properties are `compatible`, `reg`, `vdd-supply`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/amphenol,chipcap2.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/amphenol,chipcap2.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/amphenol,chipcap2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/apm,xgene-slimpro-hwmon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/apm,xgene-slimpro-hwmon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/apm,xgene-slimpro-hwmon.yaml` defines the hardware-monitor binding titled `APM X-Gene SLIMpro hwmon`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `apm,xgene-slimpro-hwmon`. Top-level properties are `compatible`, `mboxes`. Required top-level properties are `compatible`, `mboxes`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Khuong Dinh <khuong@os.amperecomputing.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/apm,xgene-slimpro-hwmon.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/apm,xgene-slimpro-hwmon.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/apm,xgene-slimpro-hwmon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml` defines the hardware-monitor binding titled `ASPEED AST2400/AST2500 PWM and Fan Tacho controller`. Description from the schema: The ASPEED PWM controller can support up to 8 PWM outputs. The ASPEED Fan Tacho controller can support up to 16 Fan tachometer inputs. There can be up to 8 fans supported. Each fan can have 1 PWM output and 1-2 Fan tach inputs. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `aspeed,ast2400-pwm-tacho`, `aspeed,ast2500-pwm-tacho`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `#cooling-cells`, `clocks`, `resets`. Required top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `clocks`, `resets`. Pattern properties are `^fan@[0-7]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Joel Stanley <joel@jms.id.au>, Andrew Jeffery <andrew@codeconstruct.com.au>. Dependencies include `/schemas/types.yaml#/definitions/uint8-array`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,g6-pwm-tach.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,g6-pwm-tach.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,g6-pwm-tach.yaml` defines the hardware-monitor binding titled `ASPEED G6 PWM and Fan Tach controller`. Description from the schema: The ASPEED PWM controller can support up to 16 PWM outputs. The ASPEED Fan Tacho controller can support up to 16 fan tach input. They are independent hardware blocks, which are different from the previous version of the ASPEED chip. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `aspeed,ast2700-pwm-tach`, `aspeed,ast2600-pwm-tach`. Top-level properties are `compatible`, `reg`, `clocks`, `resets`, `#pwm-cells`. Required top-level properties are `reg`, `clocks`, `resets`, `#pwm-cells`, `compatible`. Pattern properties are `^fan-[0-9]+$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Billy Tsai <billy_tsai@aspeedtech.com>. Dependencies include `fan-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/aspeed,g6-pwm-tach.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/aspeed,g6-pwm-tach.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,g6-pwm-tach.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml` defines the hardware-monitor binding titled `Cirrus Logic Lochnagar Audio Development Board`. Description from the schema: Lochnagar is an evaluation and development board for Cirrus Logic Smart CODEC and Amp devices. It allows the connection of most Cirrus Logic devices on mini-cards, as well as allowing connection of various application processor systems to provide a full evaluation platform. Audio system topology, clocking and power can all be controlled through the Lochnagar, allowing the device under test to be used in a variety... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `cirrus,lochnagar2-hwmon`. Top-level properties are `compatible`. Required top-level properties are `compatible`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: the main regression mode is DTS ABI drift.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/fan-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/fan-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/fan-common.yaml` defines the hardware-monitor binding titled `Common Fan Properties`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. This is a reusable common schema fragment rather than a directly matched device compatible; other bindings include it through `$ref` to share fan or hwmon property definitions. Top-level properties are `max-rpm`, `min-rpm`, `pulses-per-revolution`, `tach-div`, `target-rpm`, `fan-driving-mode`, `pwms`, `#cooling-cells`, `cooling-levels`, `tach-ch`, `label`, `fan-supply`, `reg`. Required top-level properties are none declared. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Naresh Solanki <naresh.solanki@9elements.com>, Billy Tsai <billy_tsai@aspeedtech.com>. Dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: the main regression mode is DTS ABI drift.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/fan-common.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/fan-common.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/fan-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/gmt,g762.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/gmt,g762.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/gmt,g762.yaml` defines the hardware-monitor binding titled `GMT G761/G762/G763 PWM Fan controller`. Description from the schema: GMT G761/G762/G763 PWM Fan controller. G761 supports an internal-clock hence the clocks property is optional. If not defined, internal-clock will be used. (31KHz is the clock of the internal crystal oscillator) If an optional property is not set in DT, then current value is kept unmodified (e.g. bootloader installed value). Additional information on operational parameters for the device is available in Documentati... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `gmt,g761`, `gmt,g762`, `gmt,g763`. Top-level properties are `compatible`, `reg`, `clocks`, `fan_startv`, `pwm_polarity`, `fan_gear_mode`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `if`, `then`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Christian Marangi <ansuelsmth@gmail.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/gmt,g762.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/gmt,g762.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/gmt,g762.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/gpio-fan.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/gpio-fan.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/gpio-fan.yaml` defines the hardware-monitor binding titled `Fan connected to GPIO lines`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `gpio-fan`. Top-level properties are `compatible`, `gpios`, `alarm-gpios`, `fan-supply`, `gpio-fan,speed-map`, `#cooling-cells`. Required top-level properties are `compatible`, `gpios`, `gpio-fan,speed-map`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Rob Herring <robh@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/uint32-matrix`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/gpio-fan.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/gpio-fan.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/gpio-fan.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hpe,gxp-fan-ctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hpe,gxp-fan-ctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hpe,gxp-fan-ctrl.yaml` defines the hardware-monitor binding titled `HPE GXP Fan Controller`. Description from the schema: The HPE GXP fan controller controls the fans through an external CPLD device that connects to the fans. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `hpe,gxp-fan-ctrl`. Top-level properties are `compatible`, `reg`, `reg-names`. Required top-level properties are `compatible`, `reg`, `reg-names`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Nick Hawkins <nick.hawkins@hpe.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/hpe,gxp-fan-ctrl.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/hpe,gxp-fan-ctrl.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hpe,gxp-fan-ctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hwmon-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hwmon-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hwmon-common.yaml` defines the hardware-monitor binding titled `Hardware Monitoring Devices Common Properties`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. This is a reusable common schema fragment rather than a directly matched device compatible; other bindings include it through `$ref` to share fan or hwmon property definitions. Top-level properties are `label`, `shunt-resistor-micro-ohms`. Required top-level properties are none declared. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Guenter Roeck <linux@roeck-us.net>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: the main regression mode is DTS ABI drift.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/hwmon-common.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/hwmon-common.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hwmon-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ibm,occ-hwmon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ibm,occ-hwmon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ibm,occ-hwmon.yaml` defines the hardware-monitor binding titled `IBM On-Chip Controller (OCC) accessed from a service processor`. Description from the schema: The POWER processor On-Chip Controller (OCC) helps manage power and thermals for the system. A service processor or baseboard management controller can query the OCC for it's power and thermal data to report through hwmon. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `ibm,p9-occ-hwmon`, `ibm,p10-occ-hwmon`. Top-level properties are `compatible`, `ibm,no-poll-on-init`. Required top-level properties are `compatible`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Eddie James <eajames@linux.ibm.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ibm,occ-hwmon.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ibm,occ-hwmon.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ibm,occ-hwmon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ibm,opal-sensor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ibm,opal-sensor.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ibm,opal-sensor.yaml` defines the hardware-monitor binding titled `IBM POWERNV platform sensors`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `ibm,opal-sensor-cooling-fan`, `ibm,opal-sensor-amb-temp`, `ibm,opal-sensor-power-supply`, `ibm,opal-sensor-power`. Top-level properties are `compatible`, `sensor-id`. Required top-level properties are `compatible`, `sensor-id`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ibm,opal-sensor.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ibm,opal-sensor.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ibm,opal-sensor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/iei,wt61p803-puzzle-hwmon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/iei,wt61p803-puzzle-hwmon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/iei,wt61p803-puzzle-hwmon.yaml` defines the hardware-monitor binding titled `IEI WT61P803 PUZZLE MCU HWMON module from IEI Integration Corp.`. Description from the schema: This module is a part of the IEI WT61P803 PUZZLE MFD device. For more details see Documentation/devicetree/bindings/mfd/iei,wt61p803-puzzle.yaml. The HWMON module is a sub-node of the MCU node in the Device Tree. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `iei,wt61p803-puzzle-hwmon`. Top-level properties are `compatible`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `#address-cells`, `#size-cells`. Pattern properties are `^fan-group@[0-1]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Luka Kovacic <luka.kovacic@sartura.hr>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/iei,wt61p803-puzzle-hwmon.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/iei,wt61p803-puzzle-hwmon.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/iei,wt61p803-puzzle-hwmon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/iio-hwmon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/iio-hwmon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/iio-hwmon.yaml` defines the hardware-monitor binding titled `ADC-attached Hardware Sensor`. Description from the schema: Bindings for hardware monitoring devices connected to ADC controllers supporting the Industrial I/O bindings. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `iio-hwmon`. Top-level properties are `compatible`, `io-channels`. Required top-level properties are `compatible`, `io-channels`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jonathan Cameron <jic23@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/iio-hwmon.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/iio-hwmon.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/iio-hwmon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/jedec,jc42.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/jedec,jc42.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/jedec,jc42.yaml` defines the hardware-monitor binding titled `Jedec JC-42.4 compatible temperature sensors`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 25 tokens: `jedec,jc-42.4-temp`, `adi,adt7408`, `atmel,at30ts00`, `atmel,at30tse004`, `idt,tse2002`, `idt,tse2004`, `idt,ts3000`, `idt,ts3001`, `maxim,max6604`, `microchip,mcp9804`, `microchip,mcp9805`, `microchip,mcp9808`, `microchip,mcp98243`, `microchip,mcp98244`, and 11 more. Top-level properties are `compatible`, `reg`, `smbus-timeout-disable`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jean Delvare <jdelvare@suse.com>, Guenter Roeck <linux@roeck-us.net>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/jedec,jc42.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/jedec,jc42.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/jedec,jc42.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/kontron,sl28cpld-hwmon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/kontron,sl28cpld-hwmon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/kontron,sl28cpld-hwmon.yaml` defines the hardware-monitor binding titled `Hardware monitoring driver for the sl28cpld board management controller`. Description from the schema: This module is part of the sl28cpld multi-function device. For more details see ../embedded-controller/kontron,sl28cpld.yaml. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `kontron,sl28cpld-fan`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Michael Walle <michael@walle.cc>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: the main regression mode is DTS ABI drift.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/kontron,sl28cpld-hwmon.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/kontron,sl28cpld-hwmon.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/kontron,sl28cpld-hwmon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lantiq,cputemp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lantiq,cputemp.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lantiq,cputemp.yaml` defines the hardware-monitor binding titled `Lantiq cpu temperature sensor`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `lantiq,cputemp`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Florian Eckert <fe@dev.tdt.de>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lantiq,cputemp.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lantiq,cputemp.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lantiq,cputemp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc2978.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc2978.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc2978.yaml` defines the hardware-monitor binding titled `Octal Digital Power-supply monitor/supervisor/sequencer/margin controller.`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 29 tokens: `lltc,lt7170`, `lltc,lt7171`, `lltc,ltc2972`, `lltc,ltc2974`, `lltc,ltc2975`, `lltc,ltc2977`, `lltc,ltc2978`, `lltc,ltc2979`, `lltc,ltc2980`, `lltc,ltc3880`, `lltc,ltc3882`, `lltc,ltc3883`, `lltc,ltc3884`, `lltc,ltc3886`, and 15 more. Top-level properties are `compatible`, `reg`, `regulators`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Frank Li <Frank.Li@nxp.com>. Dependencies include `/schemas/regulator/regulator.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lltc,ltc2978.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lltc,ltc2978.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc2978.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc4151.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc4151.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc4151.yaml` defines the hardware-monitor binding titled `LTC4151 High Voltage I2C Current and Voltage Monitor`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `lltc,ltc4151`. Top-level properties are `compatible`, `reg`, `shunt-resistor-micro-ohms`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lltc,ltc4151.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lltc,ltc4151.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc4151.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc4286.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc4286.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc4286.yaml` defines the hardware-monitor binding titled `LTC4286 power monitors`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `lltc,ltc4286`, `lltc,ltc4287`. Top-level properties are `compatible`, `reg`, `adi,vrange-low-enable`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Delphine CC Chiu <Delphine_CC_Chiu@Wiwynn.com>. Dependencies include `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lltc,ltc4286.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lltc,ltc4286.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lltc,ltc4286.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lm75.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lm75.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lm75.yaml` defines the hardware-monitor binding titled `LM75 hwmon sensor`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 31 tokens: `adi,adt75`, `ams,as6200`, `atmel,at30ts74`, `dallas,ds1775`, `dallas,ds75`, `dallas,ds7505`, `gmt,g751`, `national,lm75`, `national,lm75a`, `national,lm75b`, `maxim,max6625`, `maxim,max6626`, `maxim,max31725`, `maxim,max31726`, and 17 more. Top-level properties are `compatible`, `reg`, `vs-supply`, `interrupts`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jean Delvare <jdelvare@suse.com>, Guenter Roeck <linux@roeck-us.net>. Dependencies include `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lm75.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/lm75.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/lm75.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max20730.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max20730.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max20730.yaml` defines the hardware-monitor binding titled `Maxim max20730`. Description from the schema: The MAX20730 is a fully integrated, highly efficient switching regulator with PMBus for applications operating from 4.5V to 16V and requiring up to 25A (max) load. This single-chip regulator provides extremely compact, high efficiency power-delivery solutions with high-precision output voltages and excellent transient response. Datasheets: https://datasheets.maximintegrated.com/en/ds/MAX20730.pdf https://datasheet... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `maxim,max20710`, `maxim,max20730`, `maxim,max20734`, `maxim,max20743`. Top-level properties are `compatible`, `reg`, `vout-voltage-divider`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jean Delvare <jdelvare@suse.com>, Guenter Roeck <linux@roeck-us.net>. Dependencies include `/schemas/types.yaml#/definitions/uint32-array`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/maxim,max20730.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/maxim,max20730.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max20730.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max31790.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max31790.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max31790.yaml` defines the hardware-monitor binding titled `The Maxim MAX31790 Fan Controller`. Description from the schema: The MAX31790 controls the speeds of up to six fans using six independent PWM outputs. The desired fan speeds (or PWM duty cycles) are written through the I2C interface. Datasheets: https://datasheets.maximintegrated.com/en/ds/MAX31790.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `maxim,max31785`, `maxim,max31785a`, `maxim,max31785b`, `maxim,max31790`. Top-level properties are `compatible`, `reg`, `clocks`, `resets`, `#address-cells`, `#size-cells`, `#pwm-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^fan@[0-9]+$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Guenter Roeck <linux@roeck-us.net>, Chanh Nguyen <chanh@os.amperecomputing.com>. Dependencies include `fan-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/maxim,max31790.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/maxim,max31790.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max31790.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max6639.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max6639.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max6639.yaml` defines the hardware-monitor binding titled `Maxim max6639`. Description from the schema: The MAX6639 is a 2-channel temperature monitor with dual, automatic, PWM fan-speed controller. It monitors its own temperature and one external diode-connected transistor or the temperatures of two external diode-connected transistors, typically available in CPUs, FPGAs, or GPUs. Datasheets: https://datasheets.maximintegrated.com/en/ds/MAX6639-MAX6639F.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `maxim,max6639`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `#pwm-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^fan@[0-1]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Naresh Solanki <naresh.solanki@9elements.com>. Dependencies include `fan-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/maxim,max6639.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/maxim,max6639.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max6639.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max6650.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max6650.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max6650.yaml` defines the hardware-monitor binding titled `Maxim MAX6650 and MAX6651 I2C Fan Controllers`. Description from the schema: The MAX6650 and MAX6651 regulate and monitor the speed of 5VDC/12VDC burshless fans with built-in tachometers. Datasheets: https://datasheets.maximintegrated.com/en/ds/MAX6650-MAX6651.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `maxim,max6650`, `maxim,max6651`. Top-level properties are `compatible`, `reg`, `maxim,fan-microvolt`, `maxim,fan-prescale`, `maxim,fan-target-rpm`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/maxim,max6650.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/maxim,max6650.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/maxim,max6650.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,emc2305.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,emc2305.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,emc2305.yaml` defines the hardware-monitor binding titled `Microchip EMC2305 SMBus compliant PWM fan controller`. Description from the schema: Microchip EMC2301/2/3/5 pwm controller which supports up to five programmable fan control circuits. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 4 tokens: `microchip,emc2305`, `microchip,emc2303`, `microchip,emc2302`, `microchip,emc2301`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `#pwm-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^fan@[0-4]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Michael Shych <michaelsh@nvidia.com>. Dependencies include `fan-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,emc2305.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,emc2305.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,emc2305.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,lan966x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,lan966x.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,lan966x.yaml` defines the hardware-monitor binding titled `Microchip LAN966x Hardware Monitor`. Description from the schema: Microchip LAN966x temperature monitor and fan controller It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `microchip,lan9668-hwmon`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `#thermal-sensor-cells`. Required top-level properties are `compatible`, `reg`, `reg-names`, `clocks`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Michael Walle <michael@walle.cc>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,lan966x.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,lan966x.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,lan966x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,mcp3021.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,mcp3021.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,mcp3021.yaml` defines the hardware-monitor binding titled `Microchip MCP3021 A/D converter`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `microchip,mcp3021`, `microchip,mcp3221`. Top-level properties are `compatible`, `reg`, `reference-voltage-microvolt`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,mcp3021.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,mcp3021.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,mcp3021.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,mcp9982.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,mcp9982.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,mcp9982.yaml` defines the hardware-monitor binding titled `Microchip MCP998X/33 and MCP998XD/33D Temperature Monitor`. Description from the schema: The MCP998X/33 and MCP998XD/33D family is a high-accuracy 2-wire multichannel automotive temperature monitor. The datasheet can be found here: https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP998X-Family-Data-Sheet-DS20006827.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 10 tokens: `microchip,mcp9933`, `microchip,mcp9933d`, `microchip,mcp9982`, `microchip,mcp9982d`, `microchip,mcp9983`, `microchip,mcp9983d`, `microchip,mcp9984`, `microchip,mcp9984d`, `microchip,mcp9985`, `microchip,mcp9985d`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `#address-cells`, `#size-cells`, `microchip,enable-anti-parallel`, `microchip,parasitic-res-on-channel1-2`, `microchip,parasitic-res-on-channel3-4`, `microchip,power-state`, `vdd-supply`. Required top-level properties are `compatible`, `reg`, `vdd-supply`. Pattern properties are `^channel@[1-4]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Victor Duicu <victor.duicu@microchip.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; pattern property regexes can over-match or under-match child nodes; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,mcp9982.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,mcp9982.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,mcp9982.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,sparx5-temp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,sparx5-temp.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,sparx5-temp.yaml` defines the hardware-monitor binding titled `Microchip Sparx5 Temperature Monitor`. Description from the schema: Microchip Sparx5 embedded temperature monitor It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `microchip,sparx5-temp`, `microchip,lan9691-temp`. Top-level properties are `compatible`, `reg`, `clocks`, `#thermal-sensor-cells`. Required top-level properties are `compatible`, `reg`, `clocks`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Lars Povlsen <lars.povlsen@microchip.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,sparx5-temp.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/microchip,sparx5-temp.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/microchip,sparx5-temp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/moortec,mr75203.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/moortec,mr75203.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/moortec,mr75203.yaml` defines the hardware-monitor binding titled `Moortec Semiconductor MR75203 PVT Controller`. Description from the schema: A Moortec PVT (Process, Voltage, Temperature) monitoring logic design can include many different units. Such a design will usually consists of several Moortec's embedded analog IPs, and a single Moortec controller (mr75203) to configure and control the IPs. Some of the Moortec's analog hard IPs that can be used in a design: *) Temperature Sensor (TS) - used to monitor core temperature (e.g. mr74137). *) Voltage Mo... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `moortec,mr75203`. Top-level properties are `compatible`, `reg`, `reg-names`, `intel,vm-map`, `clocks`, `resets`, `#thermal-sensor-cells`, `moortec,vm-active-channels`, `moortec,vm-pre-scaler-x2`, `moortec,ts-series`, `moortec,ts-coeff-g`, `moortec,ts-coeff-h`, `moortec,ts-coeff-cal5`, `moortec,ts-coeff-j`. Required top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `#thermal-sensor-cells`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Rahul Tanwar <rtanwar@maxlinear.com>. Dependencies include `/schemas/types.yaml#/definitions/int32`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint8-array`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/moortec,mr75203.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/moortec,mr75203.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/moortec,mr75203.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/national,lm90.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/national,lm90.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/national,lm90.yaml` defines the hardware-monitor binding titled `LM90 series thermometer`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 31 tokens: `adi,adm1032`, `adi,adt7461`, `adi,adt7461a`, `adi,adt7481`, `dallas,max6646`, `dallas,max6647`, `dallas,max6649`, `dallas,max6654`, `dallas,max6657`, `dallas,max6658`, `dallas,max6659`, `dallas,max6680`, `dallas,max6681`, `dallas,max6695`, and 17 more. Top-level properties are `compatible`, `interrupts`, `reg`, `#thermal-sensor-cells`, `#address-cells`, `#size-cells`, `vcc-supply`, `ti,extended-range-enable`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^channel@([0-2])$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jean Delvare <jdelvare@suse.com>, Guenter Roeck <linux@roeck-us.net>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; pattern property regexes can over-match or under-match child nodes; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/national,lm90.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/national,lm90.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/national,lm90.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml` defines the hardware-monitor binding titled `NTC thermistor temperature sensors`. Description from the schema: Thermistors with negative temperature coefficient (NTC) are resistors that vary in resistance in an often non-linear way in relation to temperature. The negative temperature coefficient means that the resistance decreases as the temperature rises. Since the relationship between resistance and temperature is non-linear, software drivers most often need to use a look up table and interpolation to get from resistance... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 16 branches with 16 tokens: `epcos,b57330v2103`, `epcos,b57891s0103`, `murata,ncp15wb473`, `murata,ncp18wb473`, `murata,ncp21wb473`, `murata,ncp03wb473`, `murata,ncp15wl333`, `murata,ncp03wf104`, `murata,ncp15xh103`, `murata,ncp18wm474`, `samsung,1404-001221`, `ntc,ncp15wb473`, `ntc,ncp18wb473`, `ntc,ncp21wb473`, and 2 more. Top-level properties are `$nodename`, `compatible`, `#thermal-sensor-cells`, `pullup-uv`, `pullup-ohm`, `pulldown-ohm`, `connected-positive`, `io-channels`. Required top-level properties are `compatible`, `pullup-uv`, `pullup-ohm`, `pulldown-ohm`, `io-channels`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct6775.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct6775.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct6775.yaml` defines the hardware-monitor binding titled `Nuvoton NCT6775 and compatible Super I/O chips`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 13 tokens: `nuvoton,nct6106`, `nuvoton,nct6116`, `nuvoton,nct6775`, `nuvoton,nct6776`, `nuvoton,nct6779`, `nuvoton,nct6791`, `nuvoton,nct6792`, `nuvoton,nct6793`, `nuvoton,nct6795`, `nuvoton,nct6796`, `nuvoton,nct6797`, `nuvoton,nct6798`, `nuvoton,nct6799`. Top-level properties are `compatible`, `reg`, `nuvoton,tsi-channel-mask`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Zev Weiss <zev@bewilderbeest.net>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nuvoton,nct6775.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nuvoton,nct6775.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct6775.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct7363.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct7363.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct7363.yaml` defines the hardware-monitor binding titled `Nuvoton NCT7363Y Hardware Monitoring IC`. Description from the schema: The NCT7363Y is a fan controller which provides up to 16 independent FAN input monitors, and up to 16 independent PWM outputs with SMBus interface. Datasheets: Available from Nuvoton upon request It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `nuvoton,nct7363`, `nuvoton,nct7362`. Top-level properties are `compatible`, `reg`, `#pwm-cells`. Required top-level properties are `compatible`, `reg`, `#pwm-cells`. Pattern properties are `^fan-[0-9]+$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Ban Feng <kcfeng0@nuvoton.com>. Dependencies include `fan-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nuvoton,nct7363.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nuvoton,nct7363.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct7363.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct7802.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct7802.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct7802.yaml` defines the hardware-monitor binding titled `Nuvoton NCT7802Y Hardware Monitoring IC`. Description from the schema: The NCT7802Y is a hardware monitor IC which supports one on-die and up to 5 remote temperature sensors with SMBus interface. Datasheets: https://www.nuvoton.com/export/resource-files/Nuvoton_NCT7802Y_Datasheet_V12.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `nuvoton,nct7802`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^channel@[0-3]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Guenter Roeck <linux@roeck-us.net>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nuvoton,nct7802.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nuvoton,nct7802.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,nct7802.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,npcm750-pwm-fan.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,npcm750-pwm-fan.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,npcm750-pwm-fan.yaml` defines the hardware-monitor binding titled `Nuvoton NPCM7xx/NPCM8xx PWM and Fan Tach Controller`. Description from the schema: The NPCM7xx/NPCM8xx family includes a PWM and Fan Tachometer controller. The controller provides up to 8 (NPCM7xx) or 12 (NPCM8xx) PWM channels and up to 16 tachometer inputs. It is used for fan speed control and monitoring. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `nuvoton,npcm750-pwm-fan`, `nuvoton,npcm845-pwm-fan`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`. Pattern properties are `^fan@[0-9a-f]+$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Tomer Maimon <tmaimon77@gmail.com>. Dependencies include `/schemas/types.yaml#/definitions/uint8-array`, `fan-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nuvoton,npcm750-pwm-fan.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nuvoton,npcm750-pwm-fan.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nuvoton,npcm750-pwm-fan.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nxp,mc34vr500.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nxp,mc34vr500.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nxp,mc34vr500.yaml` defines the hardware-monitor binding titled `NXP MC34VR500 hwmon sensor`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `nxp,mc34vr500`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Mario Kicherer <dev@kicherer.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nxp,mc34vr500.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/nxp,mc34vr500.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/nxp,mc34vr500.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,adp1050.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,adp1050.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,adp1050.yaml` defines the PMBus hardware-monitor binding titled `Analog Devices ADP1050 digital controller with PMBus interface`. Description from the schema: The ADP1050 and similar devices are used to monitor system voltages, currents, power, and temperatures. Through the PMBus interface, the ADP1050 targets isolated power supplies and has four individual monitors for input/output voltage, input current and temperature. Datasheet: https://www.analog.com/en/products/adp1050.html https://www.analog.com/en/products/adp1051.html https://www.analog.com/en/products/adp1055.... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `adi,adp1050`, `adi,adp1051`, `adi,adp1055`, `adi,ltp8800`. Top-level properties are `compatible`, `reg`, `vcc-supply`. Required top-level properties are `compatible`, `reg`, `vcc-supply`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Radu Sabau <radu.sabau@analog.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/adi,adp1050.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/adi,adp1050.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,adp1050.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,lt3074.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,lt3074.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,lt3074.yaml` defines the PMBus hardware-monitor binding titled `Analog Devices LT3074 voltage regulator`. Description from the schema: The LT3074 is a low voltage, ultra-low noise and ultra-fast transient response linear regulator. It allows telemetry for input/output voltage, output current and temperature through the PMBus serial interface. Datasheet: https://www.analog.com/en/products/lt3074.html It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,lt3074`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Cedric Encarnacion <cedricjustine.encarnacion@analog.com>. Dependencies include `/schemas/regulator/regulator.yaml#`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/adi,lt3074.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/adi,lt3074.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,lt3074.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,max17616.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,max17616.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,max17616.yaml` defines the PMBus hardware-monitor binding titled `Analog Devices MAX17616/MAX17616A Current-Limiter with PMBus Interface`. Description from the schema: The MAX17616/MAX17616A is a 3V to 80V, 7A current-limiter with overvoltage, surge, undervoltage, reverse polarity, and loss of ground protection. It allows monitoring of input/output voltage, output current and temperature through the PMBus serial interface. Datasheet: https://www.analog.com/en/products/max17616.html It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `adi,max17616`. Top-level properties are `compatible`, `reg`, `vcc-supply`, `interrupts`. Required top-level properties are `compatible`, `reg`, `vcc-supply`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Kim Seer Paller <kimseer.paller@analog.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/adi,max17616.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/adi,max17616.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/adi,max17616.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/infineon,tda38640.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/infineon,tda38640.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/infineon,tda38640.yaml` defines the PMBus hardware-monitor binding titled `Infineon TDA38640 Synchronous Buck Regulator with SVID and I2C`. Description from the schema: The Infineon TDA38640 is a 40A Single-voltage Synchronous Buck Regulator with SVID and I2C designed for Industrial use. Datasheet: https://www.infineon.com/dgdl/Infineon-TDA38640-0000-DataSheet-v02_04-EN.pdf?fileId=8ac78c8c80027ecd018042f2337f00c9 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `infineon,tda38640`. Top-level properties are `compatible`, `reg`, `infineon,en-pin-fixed-level`, `interrupts`, `regulators`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Naresh Solanki <naresh.solanki@9elements.com>. Dependencies include `/schemas/regulator/regulator.yaml#`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/infineon,tda38640.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/infineon,tda38640.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/infineon,tda38640.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/infineon,xdp720.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/infineon,xdp720.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/infineon,xdp720.yaml` defines the PMBus hardware-monitor binding titled `Infineon XDP720 Digital eFuse Controller`. Description from the schema: The XDP720 is an eFuse with integrated current sensor and digital controller. It provides accurate system telemetry (V, I, P, T) and reports analog current at the IMON pin for post-processing. Datasheet: https://www.infineon.com/assets/row/public/documents/24/49/infineon-xdp720-001-datasheet-en.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `infineon,xdp720`. Top-level properties are `compatible`, `reg`, `infineon,rimon-micro-ohms`, `vdd-vin-supply`. Required top-level properties are `compatible`, `reg`, `vdd-vin-supply`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Ashish Yadav <ashish.yadav@infineon.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/infineon,xdp720.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/infineon,xdp720.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/infineon,xdp720.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/isil,isl68137.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/isil,isl68137.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/isil,isl68137.yaml` defines the PMBus hardware-monitor binding titled `Renesas Digital Multiphase Voltage Regulators with PMBus`. Description from the schema: Renesas digital multiphase voltage regulators with PMBus. https://www.renesas.com/en/products/power-management/multiphase-power/multiphase-dcdc-switching-controllers It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 44 tokens: `isil,isl68137`, `renesas,isl68220`, `renesas,isl68221`, `renesas,isl68222`, `renesas,isl68223`, `renesas,isl68224`, `renesas,isl68225`, `renesas,isl68226`, `renesas,isl68227`, `renesas,isl68229`, `renesas,isl68233`, `renesas,isl68239`, `renesas,isl69222`, `renesas,isl69223`, and 30 more. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^channel@([0-3])$`. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Grant Peltier <grant.peltier.jg@renesas.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32-array`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/isil,isl68137.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/isil,isl68137.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/isil,isl68137.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml` defines the PMBus hardware-monitor binding titled `MPS MP2975 Synchronous Buck Regulator`. Description from the schema: The MPS MP2971, MP2973 & MP2975 is a multi-phase voltage regulator designed for use in high-performance computing and server applications. It supports I2C/PMBus for control and monitoring. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `mps,mp2971`, `mps,mp2973`, `mps,mp2975`. Top-level properties are `compatible`, `reg`, `interrupts`, `regulators`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Naresh Solanki <naresh.solanki@9elements.com>. Dependencies include `/schemas/regulator/regulator.yaml#`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mpq8785.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mpq8785.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mpq8785.yaml` defines the PMBus hardware-monitor binding titled `Monolithic Power Systems Multiphase Voltage Regulators with PMBus`. Description from the schema: Monolithic Power Systems digital multiphase voltage regulators with PMBus. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 4 tokens: `mps,mpm3695`, `mps,mpm3695-25`, `mps,mpm82504`, `mps,mpq8785`. Top-level properties are `compatible`, `reg`, `mps,vout-fb-divider-ratio-permille`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Charles Hsu <ythsu0511@gmail.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/mps,mpq8785.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/mps,mpq8785.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mpq8785.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,lm25066.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,lm25066.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,lm25066.yaml` defines the PMBus hardware-monitor binding titled `National Semiconductor/Texas Instruments LM250x6/LM506x power-management ICs`. Description from the schema: The LM25066 family of power-management ICs (a.k.a. hot-swap controllers or eFuses in various contexts) are PMBus devices that offer temperature, current, voltage, and power monitoring. Datasheet: https://www.ti.com/lit/ds/symlink/lm25066.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 5 tokens: `ti,lm25056`, `ti,lm25066`, `ti,lm5064`, `ti,lm5066`, `ti,lm5066i`. Top-level properties are `compatible`, `reg`, `shunt-resistor-micro-ohms`, `regulators`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Zev Weiss <zev@bewilderbeest.net>. Dependencies include `/schemas/hwmon/hwmon-common.yaml#`, `/schemas/regulator/regulator.yaml#`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/ti,lm25066.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/ti,lm25066.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,lm25066.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,tps25990.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,tps25990.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,tps25990.yaml` defines the PMBus hardware-monitor binding titled `Texas Instruments TPS25990 Stackable eFuse`. Description from the schema: The TI TPS25990 is an integrated, high-current circuit protection and power management device with PMBUS interface It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `ti,tps25990`. Top-level properties are `compatible`, `reg`, `ti,rimon-micro-ohms`, `interrupts`, `regulators`. Required top-level properties are `compatible`, `reg`, `ti,rimon-micro-ohms`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Dependencies include `/schemas/regulator/regulator.yaml#`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/ti,tps25990.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/ti,tps25990.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,tps25990.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,ucd90320.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,ucd90320.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,ucd90320.yaml` defines the PMBus hardware-monitor binding titled `UCD90320 power sequencer`. Description from the schema: The UCD90320 is a 32-rail PMBus/I2C addressable power-supply sequencer and monitor. The 24 integrated ADC channels (AMONx) monitor the power supply voltage, current, and temperature. Of the 84 GPIO pins, 8 can be used as digital monitors (DMONx), 32 to enable the power supply (ENx), 24 for margining (MARx), 16 for logical GPO, and 32 GPIs for cascading, and system function. http://focus.ti.com/lit/ds/symlink/ucd90... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 7 tokens: `ti,ucd9000`, `ti,ucd9090`, `ti,ucd90120`, `ti,ucd90124`, `ti,ucd90160`, `ti,ucd90320`, `ti,ucd90910`. Top-level properties are `compatible`, `reg`, `gpio-controller`, `gpio-line-names`, `#gpio-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jim Wright <wrightj@linux.vnet.ibm.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/ti,ucd90320.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/ti,ucd90320.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/ti,ucd90320.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/vicor,pli1209bc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/vicor,pli1209bc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/vicor,pli1209bc.yaml` defines the PMBus hardware-monitor binding titled `Vicor PLI1209BC Power Regulator`. Description from the schema: The Vicor PLI1209BC is a Digital Supervisor with Isolation for use with BCM Bus Converter Modules. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `vicor,pli1209bc`. Top-level properties are `compatible`, `reg`, `regulators`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Marcello Sylvester Bauer <sylv@sylv.io>, Naresh Solanki <naresh.solanki@9elements.com>. Dependencies include `/schemas/regulator/regulator.yaml#`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/vicor,pli1209bc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/vicor,pli1209bc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/vicor,pli1209bc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pwm-fan.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pwm-fan.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pwm-fan.yaml` defines the hardware-monitor binding titled `Fan connected to PWM lines`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `pwm-fan`. Top-level properties are `compatible`, `cooling-levels`, `fan-supply`, `interrupts`, `fan-shutdown-percent`, `fan-stop-to-start-percent`, `fan-stop-to-start-us`, `pulses-per-revolution`, `pwms`, `#cooling-cells`. Required top-level properties are `compatible`, `pwms`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jean Delvare <jdelvare@suse.com>, Guenter Roeck <linux@roeck-us.net>. Dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pwm-fan.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pwm-fan.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pwm-fan.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/renesas,isl28022.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/renesas,isl28022.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/renesas,isl28022.yaml` defines the hardware-monitor binding titled `Renesas ISL28022 power monitor`. Description from the schema: The ISL28022 is a power monitor with I2C interface. The device monitors voltage, current via shunt resistor and calculated power. Datasheets: https://www.renesas.com/us/en/www/doc/datasheet/isl28022.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `renesas,isl28022`. Top-level properties are `compatible`, `reg`, `shunt-resistor-micro-ohms`, `renesas,shunt-range-microvolt`, `renesas,average-samples`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Carsten Spieß <mail@carsten-spiess.de>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/renesas,isl28022.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/renesas,isl28022.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/renesas,isl28022.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sensirion,sht15.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sensirion,sht15.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sensirion,sht15.yaml` defines the hardware-monitor binding titled `Sensirion SHT15 humidity and temperature sensor`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `sensirion,sht15`. Top-level properties are `compatible`, `clk-gpios`, `data-gpios`, `vcc-supply`. Required top-level properties are `compatible`, `clk-gpios`, `data-gpios`, `vcc-supply`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/sensirion,sht15.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/sensirion,sht15.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sensirion,sht15.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sensirion,shtc1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sensirion,shtc1.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sensirion,shtc1.yaml` defines the hardware-monitor binding titled `Sensirion SHTC1 Humidity and Temperature Sensor IC`. Description from the schema: The SHTC1, SHTW1 and SHTC3 are digital humidity and temperature sensors designed especially for battery-driven high-volume consumer electronics applications. For further information refer to Documentation/hwmon/shtc1.rst This binding document describes the binding for the hardware monitor portion of the driver. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `sensirion,shtc1`, `sensirion,shtw1`, `sensirion,shtc3`. Top-level properties are `compatible`, `reg`, `sensirion,blocking-io`, `sensirion,low-precision`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Christopher Ruehl <chris.ruehl@gtsys.com.hk>. Dependencies include `/schemas/types.yaml#/definitions/flag`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/sensirion,shtc1.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/sensirion,shtc1.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sensirion,shtc1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sophgo,sg2042-hwmon-mcu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sophgo,sg2042-hwmon-mcu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sophgo,sg2042-hwmon-mcu.yaml` defines the hardware-monitor binding titled `Sophgo SG2042 onboard MCU support`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `sophgo,sg2044-hwmon-mcu`, `sophgo,sg2042-hwmon-mcu`. Top-level properties are `compatible`, `reg`, `#thermal-sensor-cells`. Required top-level properties are `compatible`, `reg`, `#thermal-sensor-cells`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Inochi Amaoto <inochiama@outlook.com>. Dependencies include `/schemas/thermal/thermal-sensor.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/sophgo,sg2042-hwmon-mcu.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/sophgo,sg2042-hwmon-mcu.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/sophgo,sg2042-hwmon-mcu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/st,stts751.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/st,stts751.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/st,stts751.yaml` defines the hardware-monitor binding titled `STTS751 Thermometer`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `st,stts751`. Top-level properties are `compatible`, `reg`, `smbus-timeout-disable`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Dependencies include `/schemas/types.yaml#/definitions/flag`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/st,stts751.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/st,stts751.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/st,stts751.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/st,tsc1641.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/st,tsc1641.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/st,tsc1641.yaml` defines the hardware-monitor binding titled `ST Microelectronics TSC1641 I2C power monitor`. Description from the schema: TSC1641 is a 60 V, 16-bit high-precision power monitor with I2C and MIPI I3C interface Datasheets: https://www.st.com/resource/en/datasheet/tsc1641.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `st,tsc1641`. Top-level properties are `compatible`, `reg`, `interrupts`, `shunt-resistor-micro-ohms`, `st,alert-polarity-active-high`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Igor Reznichenko <igor@reznichenko.net>. Dependencies include `/schemas/types.yaml#/definitions/flag`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/st,tsc1641.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/st,tsc1641.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/st,tsc1641.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/starfive,jh71x0-temp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/starfive,jh71x0-temp.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/starfive,jh71x0-temp.yaml` defines the hardware-monitor binding titled `StarFive JH71x0 Temperature Sensor`. Description from the schema: StarFive Technology Co. JH71x0 embedded temperature sensor It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `starfive,jh7100-temp`, `starfive,jh7110-temp`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#thermal-sensor-cells`, `resets`, `reset-names`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Emil Renner Berthing <kernel@esmil.dk>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/starfive,jh71x0-temp.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/starfive,jh71x0-temp.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/starfive,jh71x0-temp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/syna,as370.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/syna,as370.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/syna,as370.yaml` defines the hardware-monitor binding titled `Synaptics AS370 PVT sensors`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `syna,as370-hwmon`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/syna,as370.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/syna,as370.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/syna,as370.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,adc128d818.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,adc128d818.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,adc128d818.yaml` defines the hardware-monitor binding titled `Texas Instruments ADC128D818 ADC System Monitor With Temperature Sensor`. Description from the schema: The ADC128D818 is a 12-Bit, 8-Channel Analog to Digital Converter (ADC) with a temperature sensor and an I2C interface. Datasheets: https://www.ti.com/product/ADC128D818 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `ti,adc128d818`. Top-level properties are `compatible`, `reg`, `ti,mode`, `vref-supply`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Dependencies include `/schemas/types.yaml#/definitions/uint8`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,adc128d818.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,adc128d818.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,adc128d818.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ads7828.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ads7828.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ads7828.yaml` defines the hardware-monitor binding titled `Texas Instruments ADS7828/ADS7830 Analog to Digital Converter (ADC)`. Description from the schema: The ADS7828 is 12-Bit, 8-Channel Sampling Analog to Digital Converter (ADC) with an I2C interface. Datasheets: https://www.ti.com/product/ADS7828 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `ti,ads7828`, `ti,ads7830`. Top-level properties are `compatible`, `reg`, `ti,differential-input`, `vref-supply`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,ads7828.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,ads7828.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ads7828.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,amc6821.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,amc6821.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,amc6821.yaml` defines the hardware-monitor binding titled `AMC6821 Intelligent Temperature Monitor and PWM Fan Controller`. Description from the schema: Intelligent temperature monitor and pulse-width modulation (PWM) fan controller. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `tsd,mule`, `ti,amc6821`. Top-level properties are `compatible`, `reg`, `i2c-mux`, `fan`, `#pwm-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `if`, `then`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Farouk Bouabid <farouk.bouabid@cherry.de>, Quentin Schulz <quentin.schulz@cherry.de>. Dependencies include `fan-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,amc6821.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,amc6821.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,amc6821.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml` defines the hardware-monitor binding titled `Texas Instruments INA209 family of power/voltage monitors`. Description from the schema: The INA209 is a high-side current shunt and power monitor with an I2C interface. Datasheets: https://www.ti.com/product/INA209 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 16 tokens: `silergy,sq52206`, `silergy,sy24655`, `ti,ina209`, `ti,ina219`, `ti,ina220`, `ti,ina226`, `ti,ina228`, `ti,ina230`, `ti,ina231`, `ti,ina233`, `ti,ina234`, `ti,ina237`, `ti,ina238`, `ti,ina260`, and 2 more. Top-level properties are `compatible`, `reg`, `#io-channel-cells`, `shunt-resistor`, `ti,shunt-gain`, `vs-supply`, `ti,alert-polarity-active-high`, `ti,maximum-expected-current-microamp`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina3221.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina3221.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina3221.yaml` defines the hardware-monitor binding titled `Texas Instruments INA3221 Current and Voltage Monitor`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `ti,ina3221`. Top-level properties are `compatible`, `reg`, `ti,single-shot`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^input@[0-2]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Jean Delvare <jdelvare@suse.com>, Guenter Roeck <linux@roeck-us.net>. Dependencies include `/schemas/types.yaml#/definitions/flag`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,ina3221.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,ina3221.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina3221.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,lm87.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,lm87.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,lm87.yaml` defines the hardware-monitor binding titled `Texas Instruments LM87 Hardware Monitor`. Description from the schema: The LM87 is a serial interface system hardware monitor with remote diode temperature sensing. Datasheets: https://www.ti.com/product/LM87 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `adi,adm1024`, `ti,lm87`. Top-level properties are `compatible`, `reg`, `has-temp3`, `has-in6`, `has-in7`, `vcc-supply`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Dependencies include `/schemas/types.yaml#/definitions/flag`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,lm87.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,lm87.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,lm87.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp102.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp102.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp102.yaml` defines the hardware-monitor binding titled `TMP102 temperature sensor`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `ti,tmp102`. Top-level properties are `compatible`, `interrupts`, `reg`, `label`, `#thermal-sensor-cells`, `vcc-supply`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp102.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp102.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp102.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp108.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp108.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp108.yaml` defines the hardware-monitor binding titled `TMP108/P3T1035/P3T1085/P3T2030 temperature sensor`. Description from the schema: The TMP108 or NXP P3T Family (P3T1035, P3T1085 and P3T2030) is a digital- output temperature sensor with a dynamically-programmable limit window, and under- and over-temperature alert functions. NXP P3T Family (P3T1035, P3T1085 and P3T2030) supports I3C. Datasheets: https://www.ti.com/product/TMP108 https://www.nxp.com/docs/en/data-sheet/P3T1085UK.pdf https://www.nxp.com/docs/en/data-sheet/P3T1035XUK_P3T2030XUK.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 4 branches with 4 tokens: `nxp,p3t2030`, `nxp,p3t1035`, `nxp,p3t1085`, `ti,tmp108`. Top-level properties are `compatible`, `interrupts`, `reg`, `#thermal-sensor-cells`, `vcc-supply`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp108.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp108.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp108.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp401.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp401.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp401.yaml` defines the hardware-monitor binding titled `TMP401, TPM411 and TMP43x temperature sensor`. Description from the schema: ±1°C Remote and Local temperature sensor Datasheets: https://www.ti.com/lit/ds/symlink/tmp401.pdf https://www.ti.com/lit/ds/symlink/tmp411.pdf https://www.ti.com/lit/ds/symlink/tmp431.pdf https://www.ti.com/lit/ds/symlink/tmp435.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 5 tokens: `ti,tmp401`, `ti,tmp411`, `ti,tmp431`, `ti,tmp432`, `ti,tmp435`. Top-level properties are `compatible`, `reg`, `ti,extended-range-enable`, `ti,n-factor`, `ti,beta-compensation`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Guenter Roeck <linux@roeck-us.net>. Dependencies include `/schemas/types.yaml#/definitions/int32`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp401.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp401.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp401.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp421.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp421.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp421.yaml` defines the hardware-monitor binding titled `TMP42x/TMP44x temperature sensor`. Description from the schema: ±1°C Remote and Local temperature sensor https://www.ti.com/lit/ds/symlink/tmp422.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 5 tokens: `ti,tmp421`, `ti,tmp422`, `ti,tmp423`, `ti,tmp441`, `ti,tmp442`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^channel@([0-3])$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Guenter Roeck <linux@roeck-us.net>. Dependencies include `/schemas/types.yaml#/definitions/int32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp421.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp421.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp421.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp464.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp464.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp464.yaml` defines the hardware-monitor binding titled `TMP464 and TMP468 temperature sensors`. Description from the schema: ±0.0625°C Remote and Local temperature sensor https://www.ti.com/lit/ds/symlink/tmp464.pdf https://www.ti.com/lit/ds/symlink/tmp468.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `ti,tmp464`, `ti,tmp468`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^channel@([0-8])$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Guenter Roeck <linux@roeck-us.net>. Dependencies include `/schemas/types.yaml#/definitions/int32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp464.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp464.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp464.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp513.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp513.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp513.yaml` defines the hardware-monitor binding titled `TMP513/512 system monitor sensor`. Description from the schema: The TMP512 (dual-channel) and TMP513 (triple-channel) are system monitors that include remote sensors, a local temperature sensor, and a high-side current shunt monitor. These system monitors have the capability of measuring remote temperatures, on-chip temperatures, and system voltage/power/current consumption. Datasheets: https://www.ti.com/lit/gpn/tmp513 https://www.ti.com/lit/gpn/tmp512 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `ti,tmp512`, `ti,tmp513`. Top-level properties are `compatible`, `reg`, `shunt-resistor-micro-ohms`, `ti,pga-gain`, `ti,bus-range-microvolt`, `ti,nfactor`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Eric Tremblay <etremblay@distech-controls.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp513.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tmp513.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tmp513.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tps23861.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tps23861.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tps23861.yaml` defines the hardware-monitor binding titled `TI TPS23861 PoE PSE`. Description from the schema: The TPS23861 is a IEEE 802.3at Quad Port Power-over-Ethernet PSE Controller. Datasheets: https://www.ti.com/lit/gpn/tps23861 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `ti,tps23861`. Top-level properties are `compatible`, `reg`, `shunt-resistor-micro-ohms`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Robert Marko <robert.marko@sartura.hr>. Dependencies include `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tps23861.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,tps23861.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,tps23861.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/winbond,w83781d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/winbond,w83781d.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/winbond,w83781d.yaml` defines the hardware-monitor binding titled `Winbond W83781 and compatible hardware monitor IC`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 5 tokens: `winbond,w83781d`, `winbond,w83781g`, `winbond,w83782d`, `winbond,w83783s`, `asus,as99127f`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/winbond,w83781d.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/winbond,w83781d.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/winbond,w83781d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/allwinner,sun6i-a31-p2wi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/allwinner,sun6i-a31-p2wi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/allwinner,sun6i-a31-p2wi.yaml` defines the I2C controller binding titled `Allwinner A31 P2WI (Push/Pull 2 Wires Interface)`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `allwinner,sun6i-a31-p2wi`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `clock-frequency`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/allwinner,sun6i-a31-p2wi.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/allwinner,sun6i-a31-p2wi.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/allwinner,sun6i-a31-p2wi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/amlogic,meson6-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/amlogic,meson6-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/amlogic,meson6-i2c.yaml` defines the I2C controller binding titled `Amlogic Meson I2C Controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 4 tokens: `amlogic,t7-i2c`, `amlogic,meson-axg-i2c`, `amlogic,meson6-i2c`, `amlogic,meson-gxbb-i2c`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Neil Armstrong <neil.armstrong@linaro.org>, Beniamino Galvani <b.galvani@gmail.com>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/amlogic,meson6-i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/amlogic,meson6-i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/amlogic,meson6-i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/apm,xgene-slimpro-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/apm,xgene-slimpro-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/apm,xgene-slimpro-i2c.yaml` defines the I2C controller binding titled `APM X-Gene SLIMpro Mailbox I2C`. Description from the schema: An I2C controller accessed over the "SLIMpro" mailbox. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `apm,xgene-slimpro-i2c`. Top-level properties are `compatible`, `mboxes`. Required top-level properties are `compatible`, `mboxes`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Khuong Dinh <khuong@os.amperecomputing.com>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/apm,xgene-slimpro-i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/apm,xgene-slimpro-i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/apm,xgene-slimpro-i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/apple,i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/apple,i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/apple,i2c.yaml` defines the I2C controller binding titled `Apple/PASemi I2C controller`. Description from the schema: Apple SoCs such as the M1 come with a I2C controller based on the one found in machines with P. A. Semi's PWRficient processors. The bus is used to communicate with e.g. USB PD chips or the speaker amp. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 11 tokens: `apple,t6020-i2c`, `apple,t8122-i2c`, `apple,t8103-i2c`, `apple,s5l8960x-i2c`, `apple,t7000-i2c`, `apple,s8000-i2c`, `apple,t8010-i2c`, `apple,t8015-i2c`, `apple,t8112-i2c`, `apple,t6000-i2c`, `apple,i2c`. Top-level properties are `compatible`, `reg`, `clocks`, `interrupts`, `clock-frequency`, `power-domains`. Required top-level properties are `compatible`, `reg`, `clocks`, `interrupts`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Sven Peter <sven@svenpeter.dev>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/apple,i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/apple,i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/apple,i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/arm,i2c-versatile.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/arm,i2c-versatile.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/arm,i2c-versatile.yaml` defines the I2C controller binding titled `I2C Controller on ARM Ltd development platforms`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses a single `const` with 1 token: `arm,versatile-i2c`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/arm,i2c-versatile.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/arm,i2c-versatile.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/arm,i2c-versatile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/aspeed,i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/aspeed,i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/aspeed,i2c.yaml` defines the I2C controller binding titled `ASPEED I2C on the AST24XX, AST25XX, and AST26XX SoCs`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `aspeed,ast2400-i2c-bus`, `aspeed,ast2500-i2c-bus`, `aspeed,ast2600-i2c-bus`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `bus-frequency`. Required top-level properties are `reg`, `compatible`, `clocks`, `resets`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Rayn Chen <rayn_chen@aspeedtech.com>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/aspeed,i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/aspeed,i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/aspeed,i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/atmel,at91sam-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/atmel,at91sam-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/atmel,at91sam-i2c.yaml` defines the I2C controller binding titled `I2C for Atmel/Microchip platforms`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 13 tokens: `atmel,at91rm9200-i2c`, `atmel,at91sam9261-i2c`, `atmel,at91sam9260-i2c`, `atmel,at91sam9g20-i2c`, `atmel,at91sam9g10-i2c`, `atmel,at91sam9x5-i2c`, `atmel,sama5d4-i2c`, `atmel,sama5d2-i2c`, `microchip,sam9x60-i2c`, `microchip,lan9691-i2c`, `microchip,sama7d65-i2c`, `microchip,sama7g5-i2c`, `microchip,sam9x7-i2c`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-frequency`, `dmas`, `dma-names`, `atmel,fifo-size`, `scl-gpios`, `sda-gpios`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Alexandre Belloni <alexandre.belloni@bootlin.com>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/atmel,at91sam-i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/atmel,at91sam-i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/atmel,at91sam-i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml` defines the I2C controller binding titled `Broadcom BCM2835 I2C controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `brcm,bcm2835-i2c`, `brcm,bcm2711-i2c`. Top-level properties are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `clock-frequency`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Stephen Warren <swarren@wwwdotorg.org>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,brcmstb-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,brcmstb-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,brcmstb-i2c.yaml` defines the I2C controller binding titled `Broadcom STB BSC IIC Master Controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `brcm,bcm2711-hdmi-i2c`, `brcm,brcmstb-i2c`, `brcm,brcmper-i2c`. Top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clock-frequency`. Required top-level properties are `compatible`, `reg`, `clock-frequency`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, `if`, `then`, `else`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Kamal Dasu <kdasu.kdev@gmail.com>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,brcmstb-i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,brcmstb-i2c.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,brcmstb-i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,iproc-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,iproc-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,iproc-i2c.yaml` defines the I2C controller binding titled `Broadcom iProc I2C controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `brcm,iproc-i2c`, `brcm,iproc-nic-i2c`. Top-level properties are `compatible`, `reg`, `clock-frequency`, `interrupts`, `brcm,ape-hsls-addr-mask`. Required top-level properties are `reg`, `clock-frequency`, `#address-cells`, `#size-cells`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Rafał Miłecki <rafal@milecki.pl>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,iproc-i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,iproc-i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,iproc-i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,kona-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,kona-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,kona-i2c.yaml` defines the I2C controller binding titled `Broadcom Kona family I2C controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an ordered fallback `items` sequence with 4 tokens: `brcm,bcm11351-i2c`, `brcm,bcm21664-i2c`, `brcm,bcm23550-i2c`, `brcm,kona-i2c`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-frequency`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-frequency`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Florian Fainelli <f.fainelli@gmail.com>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,kona-i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,kona-i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,kona-i2c.yaml -->
