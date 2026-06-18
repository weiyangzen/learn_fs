# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp1-rcc.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
STMicroelectronics STM32MP1 Reset Clock Controller. It lives under `clock` bindings and gives
dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: The RCC IP is both a reset and a clock controller. RCC
makes also power management (resume/supend and wakeup interrupt). Please also refer to reset.txt
for common reset controller binding usage. This binding uses common clock bindings
Documentation/devicetree/bindings/clock/clock-bindings.txt Specifying clocks =================
All available clocks are defined as preprocessor macros in include/dt-
bindings/clock/stm32mp1-clks.h header and can be used in device tree sources. Specifying
softreset control of devices ======================================= Device nodes should sp...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/st,stm32mp1-rcc.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `syscon`, `st,stm32mp1-rcc-secure`, `st,stm32mp1-rcc`, `st,stm32mp13-rcc`.
- Required properties: `#clock-cells`, `#reset-cells`, `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `clocks` (1-5 items); `clock-names` (1-5 items); `#clock-cells` (const `1`); `#reset-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 1 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. `additionalProperties: false` closes the top-
level node to undeclared keys.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: No `$ref` dependencies were found in the parsed schema..
- Example/header integration: `dt-bindings/clock/stm32mp1-clks.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `#clock-cells`, `#reset-cells`,
`compatible`, `reg` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp1-rcc.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp1-rcc.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/stm32mp1-clks.h>; rcc: rcc@50000000 {; compatible = "st,stm32mp1-rcc-secure", "syscon";; reg = <0x50000000 0x1000>;; #clock-cells = <1>;
