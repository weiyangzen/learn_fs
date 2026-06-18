# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32-rcc.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
STMicroelectronics STM32 Reset Clock Controller. It lives under `clock` bindings and gives dt-
schema a machine-readable contract for matching hardware nodes before those nodes reach kernel
drivers. The description says: The RCC IP is both a reset and a clock controller. The reset
phandle argument is the bit number within the RCC registers bank, starting from RCC base
address.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/st,stm32-rcc.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `st,stm32-rcc`, `st,stm32f42xx-rcc`, `st,stm32f746-rcc`, `st,stm32h743-rcc`, `st,stm32f469-rcc`, `st,stm32f769-rcc`.
- Required properties: `compatible`, `reg`, `#reset-cells`, `#clock-cells`, `clocks`, `st,syscfg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: `st,syscfg`, `st,ssc-modfreq-hz`, `st,ssc-moddepth-permyriad`, `st,ssc-modmethod`.
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `clocks` (2-3 items); `#clock-cells` (enum `1`, `2`); `st,syscfg` (ref `/schemas/types.yaml#/definitions/phandle`; Phandle to system configuration controller. It can be used to control the power domain circuitry.); `st,ssc-modfreq-hz` (The modulation frequency for main PLL (in Hz)); `st,ssc-moddepth-permyriad` (ref `/schemas/types.yaml#/definitions/uint32`; The modulation rate for main PLL (in permyriad, i.e. 0.01%)); `st,ssc-modmethod` (ref `/schemas/types.yaml#/definitions/string`; The modulation techniques for main PLL.); `#reset-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 1 `oneOf`, 0 `anyOf`, and 1 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/string`.
- Textual schema references: `/schemas/clock/st,stm32-rcc.yaml`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#reset-cells`,
`#clock-cells`, `clocks`, `st,syscfg` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32-rcc.yaml` to parse this YAML, validate meta-schema rules, and compile its 2 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32-rcc.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@40023800 {; compatible = "st,stm32f42xx-rcc", "st,stm32-rcc";; reg = <0x40023800 0x400>;; #clock-cells = <2>;; #reset-cells = <1>;
