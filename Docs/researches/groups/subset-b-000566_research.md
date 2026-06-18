# subset-b-000566 Research

Grouped source research for the subset B work item. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/samsung,s5pv210-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/samsung,s5pv210-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Samsung S5P6442/S5PC110/S5PV210 SoC clock controller. It lives under `clock` bindings and gives
dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: Expected external clocks, defined in DTS as fixed-rate
clocks with a matching name:: - "xxti" - external crystal oscillator connected to XXTI and XXTO
pins of the SoC, - "xusbxti" - external crystal oscillator connected to XUSBXTI and XUSBXTO pins
of the SoC, All available clocks are defined as preprocessor macros in include/dt-
bindings/clock/s5pv210.h header.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/samsung,s5pv210-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `samsung,s5pv210-clock`, `samsung,s5p6442-clock`.
- Required properties: `compatible`, `#clock-cells`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `samsung,s5pv210-clock`, `samsung,s5p6442-clock`); `reg` (max 1 items); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/s5pv210.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `reg`
should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/samsung,s5pv210-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/samsung,s5pv210-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/s5pv210.h>; xxti: clock-0 {; compatible = "fixed-clock";; clock-frequency = <0>;; clock-output-names = "xxti";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/samsung,s5pv210-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu540-prci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu540-prci.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
SiFive FU540 Power Reset Clock Interrupt Controller (PRCI). It lives under `clock` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: On the FU540 family of SoCs, most system-wide clock and
reset integration is via the PRCI IP block. The clock consumer should specify the desired clock
via the clock ID macros defined in include/dt-bindings/clock/sifive-fu540-prci.h. These macros
begin with PRCI_CLK_. The hfclk and rtcclk nodes are required, and represent physical crystals
or resonators located on the PCB. These nodes should be present underneath /, rather than /soc.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sifive/fu540-prci.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sifive,fu540-c000-prci`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `sifive,fu540-c000-prci`); `reg` (max 1 items); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/sifive/fu540-prci.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu540-prci.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu540-prci.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: prci: clock-controller@10000000 {; compatible = "sifive,fu540-c000-prci";; reg = <0x10000000 0x1000>;; clocks = <&hfclk>, <&rtcclk>;; #clock-cells = <1>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu540-prci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu740-prci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu740-prci.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
SiFive FU740 Power Reset Clock Interrupt Controller (PRCI). It lives under `clock` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: On the FU740 family of SoCs, most system-wide clock and
reset integration is via the PRCI IP block. The clock consumer should specify the desired clock
via the clock ID macros defined in include/dt-bindings/clock/sifive-fu740-prci.h. These macros
begin with PRCI_CLK_. The hfclk and rtcclk nodes are required, and represent physical crystals
or resonators located on the PCB. These nodes should be present underneath /, rather than /soc.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sifive/fu740-prci.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sifive,fu740-c000-prci`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `sifive,fu740-c000-prci`); `reg` (max 1 items); `#clock-cells` (const `1`); `#reset-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/sifive/fu740-prci.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu740-prci.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu740-prci.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: prci: clock-controller@10000000 {; compatible = "sifive,fu740-c000-prci";; reg = <0x10000000 0x1000>;; clocks = <&hfclk>, <&rtcclk>;; #clock-cells = <1>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sifive/fu740-prci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5341.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5341.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Silicon Labs Si5340/1/2/4/5 programmable i2c clock generator. It lives under `clock` bindings
and gives dt-schema a machine-readable contract for matching hardware nodes before those nodes
reach kernel drivers. The description says: Silicon Labs Si5340, Si5341 Si5342, Si5344 and
Si5345 programmable i2c clock generator. Reference [1] Si5341 Data Sheet
https://www.silabs.com/documents/public/data-sheets/Si5341-40-D-DataSheet.pdf [2] Si5341
Reference Manual https://www.silabs.com/documents/public/reference-manuals/Si5341-40-D-RM.pdf
[3] Si5345 Reference Manual https://www.silabs.com/documents/public/reference-
manuals/Si5345-44-42-D-RM.pdf The Si5341 and Si5340 are programmable i2c clock generators with
up to 10 output clocks. The chip contains a PLL that sources 5 (or 4) multisynth clocks,
which...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/silabs,si5341.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `silabs,si5340`, `silabs,si5341`, `silabs,si5342`, `silabs,si5344`, `silabs,si5345`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: `silabs,pll-m-num`, `silabs,pll-m-den`, `silabs,reprogram`, `silabs,xaxb-ext-clk`, `silabs,iovdd-33`.
- Other declared properties: `vdd-supply`, `vdda-supply`, `vdds-supply`.
- Child-node or pattern API: `^vddo[0-9]-supply$`; `^out@[0-9]$` requiring `reg`.
- Property detail signals: `compatible` (enum `silabs,si5340`, `silabs,si5341`, `silabs,si5342`, `silabs,si5344`, `silabs,si5345`); `reg` (max 1 items); `interrupts` (max 1 items; Interrupt for INTRb pin); `clocks` (1-4 items); `clock-names` (min 1 items); `#clock-cells` (const `2`; The first value is "0" for outputs, "1" for synthesizers. The second value is the output or synthesizer index.); `#address-cells` (const `1`); `#size-cells` (const `0`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/silabs,si5341.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`#address-cells`, `#size-cells`, `clocks`, `clock-names` should be caught by dt-schema before
runtime.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5341.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5341.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: i2c {; #address-cells = <1>;; #size-cells = <0>;; clock-generator@74 {; reg = <0x74>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5341.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5351.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5351.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Silicon Labs Si5351A/B/C programmable I2C clock generators. It lives under `clock` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: The Silicon Labs Si5351A/B/C are programmable I2C clock
generators with up to 8 outputs. Si5351A also has a reduced pin-count package (10-MSOP) where
only 3 output clocks are accessible. The internal structure of the clock generators can be found
in [1]. [1] Si5351A/B/C Data Sheet
https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/Si5351-B.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/silabs,si5351.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `silabs,si5351a`, `silabs,si5351a-msop`, `silabs,si5351b`, `silabs,si5351c`.
- Required properties: `reg`, `#address-cells`, `#size-cells`, `#clock-cells`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: `silabs,pll-source`, `silabs,pll-reset-mode`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: `^clkout@[0-7]$` requiring `reg`.
- Property detail signals: `compatible` (enum `silabs,si5351a`, `silabs,si5351a-msop`, `silabs,si5351b`, `silabs,si5351c`); `reg` (enum `96`, `97`); `clocks` (1-2 items); `clock-names` (min 1 items); `#clock-cells` (const `1`); `#address-cells` (const `1`); `#size-cells` (const `0`); `silabs,pll-source` (ref `/schemas/types.yaml#/definitions/uint32-matrix`; A list of cell pairs containing a PLL index and its source. Allows to overwrite clock source of the internal PLLs.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 2
`allOf`, 0 `oneOf`, 0 `anyOf`, and 3 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. `unevaluatedProperties: false` closes the
node after referenced schemas and conditional branches are evaluated.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`, `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/silabs,si5351.yaml`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-matrix`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `reg`, `#address-cells`, `#size-cells`,
`#clock-cells`, `clocks`, `clock-names` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5351.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5351.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: i2c {; #address-cells = <1>;; #size-cells = <0>;; clock-generator@60 {; compatible = "silabs,si5351a-msop";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5351.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si544.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si544.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Silicon Labs SI514/SI544 clock generator. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: Silicon Labs 514/544 programmable I2C clock generator. Details about the
device can be found in the datasheet:
https://www.silabs.com/Support%20Documents/TechnicalDocs/si514.pdf
https://www.silabs.com/documents/public/data-sheets/si544-datasheet.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/silabs,si544.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `silabs,si514`, `silabs,si544a`, `silabs,si544b`, `silabs,si544c`.
- Required properties: `compatible`, `reg`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `silabs,si514`, `silabs,si544a`, `silabs,si544b`, `silabs,si544c`); `reg` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/silabs,si544.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`
should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si544.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si544.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: i2c {; #address-cells = <1>;; #size-cells = <0>;; clock-controller@55 {; reg = <0x55>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si544.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si570.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si570.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Silicon Labs Si570/Si571/Si598/Si599 programmable I2C clock generator. It lives under `clock`
bindings and gives dt-schema a machine-readable contract for matching hardware nodes before
those nodes reach kernel drivers. The description says: Silicon Labs 570, 571, 598 and 599
programmable I2C clock generators. Details about the devices can be found in the data
sheets[1][2]. [1] Si570/571 Data Sheet
https://www.silabs.com/Support%20Documents/TechnicalDocs/si570.pdf [2] Si598/599 Data Sheet
https://www.silabs.com/Support%20Documents/TechnicalDocs/si598-99.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/silabs,si570.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `silabs,si570`, `silabs,si571`, `silabs,si598`, `silabs,si599`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `factory-fout`, `temperature-stability`.
- Top-level framework properties: `compatible`, `reg`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `silabs,skip-recall`.
- Other declared properties: `factory-fout`, `temperature-stability`, `clock-frequency`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `silabs,si570`, `silabs,si571`, `silabs,si598`, `silabs,si599`); `reg` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `silabs,skip-recall` (type `boolean`; Skip the NVM-to-RAM recall operation during boot.); `factory-fout` (ref `/schemas/types.yaml#/definitions/uint32`; Factory-set default frequency in Hz.); `temperature-stability` (enum `7`, `20`, `50`, `100`; ref `/schemas/types.yaml#/definitions/uint32`; Temperature stability of the device in PPM.); `clock-frequency` (Output frequency to generate at boot; can be reprogrammed at runtime.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/silabs,si570.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`factory-fout`, `temperature-stability` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si570.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si570.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: i2c {; #address-cells = <1>;; #size-cells = <0>;; clock-generator@5d {; compatible = "silabs,si570";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si570.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/skyworks,si521xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/skyworks,si521xx.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Skyworks Si521xx I2C PCIe clock generators. It lives under `clock` bindings and gives dt-schema
a machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: The Skyworks Si521xx are I2C PCIe clock generators providing from 4 to 9
output clocks.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/skyworks,si521xx.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `skyworks,si52144`, `skyworks,si52146`, `skyworks,si52147`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: `skyworks,out-amplitude-microvolt`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `skyworks,si52144`, `skyworks,si52146`, `skyworks,si52147`); `reg` (const `107`); `#clock-cells` (const `1`); `skyworks,out-amplitude-microvolt` (enum `300000`, `400000`, `500000`, `600000`, `700000`, `800000`, `900000`, `1000000`; Output clock signal amplitude).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/skyworks,si521xx.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/skyworks,si521xx.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/skyworks,si521xx.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: i2c {; #address-cells = <1>;; #size-cells = <0>;; clock-generator@6b {; compatible = "skyworks,si52144";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/skyworks,si521xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/socionext,uniphier-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/socionext,uniphier-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
UniPhier clock controller. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/socionext,uniphier-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `socionext,uniphier-ld4-clock`, `socionext,uniphier-pro4-clock`, `socionext,uniphier-sld8-clock`, `socionext,uniphier-pro5-clock`, `socionext,uniphier-pxs2-clock`, `socionext,uniphier-ld6b-clock`, `socionext,uniphier-ld11-clock`, `socionext,uniphier-ld20-clock`, `socionext,uniphier-pxs3-clock`, `socionext,uniphier-nx1-clock`, `socionext,uniphier-ld4-mio-clock`, `socionext,uniphier-pro4-mio-clock`, `socionext,uniphier-sld8-mio-clock`, `socionext,uniphier-pro5-sd-clock`, plus 15 more.
- Required properties: `compatible`, `#clock-cells`.
- Top-level framework properties: `compatible`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/socionext,uniphier-clock.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells` should be
caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/socionext,uniphier-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/socionext,uniphier-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller {; compatible = "socionext,uniphier-ld11-clock";; #clock-cells = <1>;; };

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/socionext,uniphier-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,cv1800-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,cv1800-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Sophgo CV1800/SG2000 Series Clock Controller. It lives under `clock` bindings and gives dt-
schema a machine-readable contract for matching hardware nodes before those nodes reach kernel
drivers. The file does not carry a long description, so its role is inferred from title, path,
and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sophgo,cv1800-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sophgo,sg2002-clk`, `sophgo,sg2000-clk`, `sophgo,cv1800-clk`, `sophgo,cv1810-clk`, `sophgo,cv1800b-clk`, `sophgo,cv1812h-clk`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `clocks` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/sophgo,cv1800.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/sophgo,cv1800-clk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,cv1800-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,cv1800-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@3002000 {; compatible = "sophgo,cv1800-clk";; reg = <0x03002000 0x1000>;; clocks = <&osc>;; #clock-cells = <1>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,cv1800-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-clkgen.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-clkgen.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Sophgo SG2042 Clock Generator for divider/mux/gate. It lives under `clock` bindings and gives
dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The file does not carry a long description, so its role is inferred from title,
path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sophgo,sg2042-clkgen.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sophgo,sg2042-clkgen`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `sophgo,sg2042-clkgen`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/sophgo,sg2042-clkgen.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/sophgo,sg2042-clkgen.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#clock-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-clkgen.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-clkgen.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@30012000 {; compatible = "sophgo,sg2042-clkgen";; reg = <0x30012000 0x1000>;; clocks = <&pllclk 0>,; <&pllclk 1>,

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-clkgen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-pll.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-pll.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Sophgo SG2042 PLL Clock Generator. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The file does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sophgo,sg2042-pll.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sophgo,sg2042-pll`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `sophgo,sg2042-pll`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/sophgo,sg2042-pll.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/sophgo,sg2042-pll.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#clock-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-pll.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-pll.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@10000000 {; compatible = "sophgo,sg2042-pll";; reg = <0x10000000 0x10000>;; clocks = <&cgi_main>, <&cgi_dpll0>, <&cgi_dpll1>;; clock-names = "cgi_main", "cgi_dpll0", "cgi_dpll1";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-pll.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-rpgate.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-rpgate.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Sophgo SG2042 Gate Clock Generator for RP(riscv processors) subsystem. It lives under `clock`
bindings and gives dt-schema a machine-readable contract for matching hardware nodes before
those nodes reach kernel drivers. The file does not carry a long description, so its role is
inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sophgo,sg2042-rpgate.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sophgo,sg2042-rpgate`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `sophgo,sg2042-rpgate`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/sophgo,sg2042-rpgate.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/sophgo,sg2042-rpgate.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#clock-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-rpgate.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-rpgate.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@20000000 {; compatible = "sophgo,sg2042-rpgate";; reg = <0x20000000 0x10000>;; clocks = <&clkgen 85>;; clock-names = "rpgate";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2042-rpgate.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2044-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2044-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Sophgo SG2044 Clock Controller. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: The Sophgo SG2044 clock controller requires an external oscillator as input
clock. All available clocks are defined as preprocessor macros in include/dt-
bindings/clock/sophgo,sg2044-clk.h

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sophgo,sg2044-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sophgo,sg2044-clk`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `sophgo,sg2044-clk`); `reg` (max 1 items); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/sophgo,sg2044-pll.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2044-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2044-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/sophgo,sg2044-pll.h>; clock-controller@50002000 {; compatible = "sophgo,sg2044-clk";; reg = <0x50002000 0x1000>;; #clock-cells = <1>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sophgo,sg2044-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/spacemit,k1-pll.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/spacemit,k1-pll.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
SpacemiT K1/K3 PLL. It lives under `clock` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The file does not
carry a long description, so its role is inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/spacemit,k1-pll.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `spacemit,k1-pll`, `spacemit,k3-pll`.
- Required properties: `compatible`, `reg`, `clocks`, `spacemit,mpmu`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: `spacemit,mpmu`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `spacemit,k1-pll`, `spacemit,k3-pll`); `reg` (max 1 items); `clocks` (External 24MHz oscillator); `#clock-cells` (const `1`; For K1 SoC, check <dt-bindings/clock/spacemit,k1-syscon.h> for valid indices. For K3 SoC, check <dt-bindings/clock/sp...); `spacemit,mpmu` (ref `/schemas/types.yaml#/definitions/phandle`; Phandle to the "Main PMU (MPMU)" syscon. It is used to check PLL lock status.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/phandle`.
- Textual schema references: `/schemas/clock/spacemit,k1-pll.yaml`, `/schemas/types.yaml#/definitions/phandle`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`,
`spacemit,mpmu`, `#clock-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/spacemit,k1-pll.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/spacemit,k1-pll.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@d4090000 {; compatible = "spacemit,k1-pll";; reg = <0xd4090000 0x1000>;; clocks = <&vctcxo_24m>;; spacemit,mpmu = <&sysctl_mpmu>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/spacemit,k1-pll.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9860-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9860-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Spreadtrum SC9860 clock. It lives under `clock` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The file does not
carry a long description, so its role is inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sprd,sc9860-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sprd,sc9860-agcp-gate`, `sprd,sc9860-aonsecure-clk`, `sprd,sc9860-aon-gate`, `sprd,sc9860-aon-prediv`, `sprd,sc9860-apahb-gate`, `sprd,sc9860-apapb-gate`, `sprd,sc9860-ap-clk`, `sprd,sc9860-cam-clk`, `sprd,sc9860-cam-gate`, `sprd,sc9860-disp-clk`, `sprd,sc9860-disp-gate`, `sprd,sc9860-gpu-clk`, `sprd,sc9860-pll`, `sprd,sc9860-pmu-gate`, plus 2 more.
- Required properties: `compatible`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: `sprd,syscon`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `sprd,sc9860-agcp-gate`, `sprd,sc9860-aonsecure-clk`, `sprd,sc9860-aon-gate`, `sprd,sc9860-aon-prediv`, `sprd,sc9860-apahb-gate`, `sprd,sc9860-apapb-gate`, `sprd,sc9860-ap-clk`, `sprd,sc9860-cam-clk` (+8 more)); `reg` (max 1 items); `clocks` (1-3 items); `#clock-cells` (const `1`); `sprd,syscon` (ref `/schemas/types.yaml#/definitions/phandle`; phandle to the syscon which is in the same address area with the clock, and so we can get regmap for the clocks from...).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 0 `oneOf`, 0 `anyOf`, and 4 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/phandle`.
- Textual schema references: `/schemas/clock/sprd,sc9860-clk.yaml`, `/schemas/types.yaml#/definitions/phandle`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `clocks`, `#clock-cells`
should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9860-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9860-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: soc {; #address-cells = <2>;; #size-cells = <2>;; clock-controller@20000000 {; compatible = "sprd,sc9860-ap-clk";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9860-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9863a-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9863a-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
SC9863A Clock Control Unit. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sprd,sc9863a-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sprd,sc9863a-ap-clk`, `sprd,sc9863a-aon-clk`, `sprd,sc9863a-apahb-gate`, `sprd,sc9863a-pmu-gate`, `sprd,sc9863a-aonapb-gate`, `sprd,sc9863a-pll`, `sprd,sc9863a-mpll`, `sprd,sc9863a-rpll`, `sprd,sc9863a-dpll`, `sprd,sc9863a-mm-gate`, `sprd,sc9863a-mm-clk`, `sprd,sc9863a-apapb-gate`.
- Required properties: `compatible`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `sprd,sc9863a-ap-clk`, `sprd,sc9863a-aon-clk`, `sprd,sc9863a-apahb-gate`, `sprd,sc9863a-pmu-gate`, `sprd,sc9863a-aonapb-gate`, `sprd,sc9863a-pll`, `sprd,sc9863a-mpll`, `sprd,sc9863a-rpll` (+4 more)); `reg` (max 1 items); `clocks` (1-4 items; The input parent clock(s) phandle for this clock, only list fixed clocks which are declared in devicetree.); `clock-names` (min 1 items); `#clock-cells` (const `1`).

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
- Textual schema references: `/schemas/clock/sprd,sc9863a-clk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells` should be
caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9863a-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 2 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9863a-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: ap_clk: clock-controller@21500000 {; compatible = "sprd,sc9863a-ap-clk";; reg = <0x21500000 0x1000>;; clocks = <&ext_26m>, <&ext_32k>;; clock-names = "ext-26m", "ext-32k";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9863a-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,ums512-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,ums512-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
UMS512 Soc clock controller. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sprd,ums512-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sprd,ums512-apahb-gate`, `sprd,ums512-ap-clk`, `sprd,ums512-aonapb-clk`, `sprd,ums512-pmu-gate`, `sprd,ums512-g0-pll`, `sprd,ums512-g2-pll`, `sprd,ums512-g3-pll`, `sprd,ums512-gc-pll`, `sprd,ums512-aon-gate`, `sprd,ums512-audcpapb-gate`, `sprd,ums512-audcpahb-gate`, `sprd,ums512-gpu-clk`, `sprd,ums512-mm-clk`, `sprd,ums512-mm-gate-clk`, plus 1 more.
- Required properties: `compatible`, `#clock-cells`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `sprd,ums512-apahb-gate`, `sprd,ums512-ap-clk`, `sprd,ums512-aonapb-clk`, `sprd,ums512-pmu-gate`, `sprd,ums512-g0-pll`, `sprd,ums512-g2-pll`, `sprd,ums512-g3-pll`, `sprd,ums512-gc-pll` (+7 more)); `reg` (max 1 items); `clocks` (1-4 items; The input parent clock(s) phandle for the clock, only list fixed clocks which are declared in devicetree.); `clock-names` (min 1 items); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/sprd,ums512-clk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `reg`
should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,ums512-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,ums512-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: ap_clk: clock-controller@20200000 {; compatible = "sprd,ums512-ap-clk";; reg = <0x20200000 0x1000>;; clocks = <&ext_26m>;; clock-names = "ext-26m";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,ums512-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32-rcc.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32-rcc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp1-rcc.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp1-rcc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp21-rcc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp21-rcc.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
STM32MP21 Reset Clock Controller. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: The RCC hardware block is both a reset and a clock controller. RCC makes also
power management (resume/suspend). See also: include/dt-bindings/clock/st,stm32mp21-rcc.h
include/dt-bindings/reset/st,stm32mp21-rcc.h

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/st,stm32mp21-rcc.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `st,stm32mp21-rcc`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `#reset-cells`, `clocks`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`, `access-controllers`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `st,stm32mp21-rcc`); `reg` (max 1 items); `#clock-cells` (const `1`); `#reset-cells` (const `1`); `access-controllers` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/st,stm32mp21-rcc.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`#reset-cells`, `clocks` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp21-rcc.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp21-rcc.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/st,stm32mp21-rcc.h>; clock-controller@44200000 {; compatible = "st,stm32mp21-rcc";; reg = <0x44200000 0x10000>;; #clock-cells = <1>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp21-rcc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp25-rcc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp25-rcc.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
STM32MP25 Reset Clock Controller. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: The RCC hardware block is both a reset and a clock controller. RCC makes also
power management (resume/suspend). See also: include/dt-bindings/clock/st,stm32mp25-rcc.h
include/dt-bindings/reset/st,stm32mp25-rcc.h

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/st,stm32mp25-rcc.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `st,stm32mp25-rcc`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `#reset-cells`, `clocks`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`, `access-controllers`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `st,stm32mp25-rcc`); `reg` (max 1 items); `#clock-cells` (const `1`); `#reset-cells` (const `1`); `access-controllers` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/st,stm32mp25-rcc.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`#reset-cells`, `clocks` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp25-rcc.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp25-rcc.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/st,stm32mp25-rcc.h>; clock-controller@44200000 {; compatible = "st,stm32mp25-rcc";; reg = <0x44200000 0x10000>;; #clock-cells = <1>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/st,stm32mp25-rcc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-audclk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-audclk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
StarFive JH7100 Audio Clock Generator. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The file does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/starfive,jh7100-audclk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `starfive,jh7100-audclk`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `starfive,jh7100-audclk`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/starfive-jh7100-audio.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/starfive-jh7100.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#clock-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-audclk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-audclk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/starfive-jh7100.h>; clock-controller@10480000 {; compatible = "starfive,jh7100-audclk";; reg = <0x10480000 0x10000>;; clocks = <&clkgen JH7100_CLK_AUDIO_SRC>,

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-audclk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-clkgen.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-clkgen.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
StarFive JH7100 Clock Generator. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/starfive,jh7100-clkgen.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `starfive,jh7100-clkgen`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `starfive,jh7100-clkgen`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/starfive-jh7100.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/starfive,jh7100-clkgen.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#clock-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-clkgen.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-clkgen.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@11800000 {; compatible = "starfive,jh7100-clkgen";; reg = <0x11800000 0x10000>;; clocks = <&osc_sys>, <&osc_aud>, <&gmac_rmii_ref>, <&gmac_gr_mii_rxclk>;; clock-names = "osc_sys", "osc_aud", "gmac_rmi...

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7100-clkgen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-aoncrg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-aoncrg.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
StarFive JH7110 Always-On Clock and Reset Generator. It lives under `clock` bindings and gives
dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The file does not carry a long description, so its role is inferred from title,
path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/starfive,jh7110-aoncrg.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `starfive,jh7110-aoncrg`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `starfive,jh7110-aoncrg`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/starfive,jh7110-crg.h> for valid indices.); `#reset-cells` (const `1`; See <dt-bindings/reset/starfive,jh7110-crg.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 2 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/starfive,jh7110-crg.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#clock-cells`, `#reset-cells` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-aoncrg.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-aoncrg.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/starfive,jh7110-crg.h>; clock-controller@17000000 {; compatible = "starfive,jh7110-aoncrg";; reg = <0x17000000 0x10000>;; clocks = <&osc>, <&gmac0_rmii_refin>,

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-aoncrg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-ispcrg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-ispcrg.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
StarFive JH7110 Image-Signal-Process Clock and Reset Generator. It lives under `clock` bindings
and gives dt-schema a machine-readable contract for matching hardware nodes before those nodes
reach kernel drivers. The file does not carry a long description, so its role is inferred from
title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/starfive,jh7110-ispcrg.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `starfive,jh7110-ispcrg`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `#clock-cells`, `#reset-cells`, `power-domains`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `resets`, `power-domains`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `starfive,jh7110-ispcrg`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/starfive,jh7110-crg.h> for valid indices.); `power-domains` (max 1 items; ISP domain power); `#reset-cells` (const `1`; See <dt-bindings/reset/starfive,jh7110-crg.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/starfive,jh7110-crg.h`, `dt-bindings/power/starfive,jh7110-pmu.h`, `dt-bindings/reset/starfive,jh7110-crg.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `resets`, `#clock-cells`, `#reset-cells`, `power-domains` should be caught by dt-schema
before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-ispcrg.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-ispcrg.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/starfive,jh7110-crg.h>; #include <dt-bindings/power/starfive,jh7110-pmu.h>; #include <dt-bindings/reset/starfive,jh7110-crg.h>; ispcrg: clock-controller@19810000 {; compatible = "starfive,j...

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-ispcrg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-pll.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-pll.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
StarFive JH7110 PLL Clock Generator. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: These PLLs are high speed, low jitter frequency synthesizers in the
JH7110. Each PLL works in integer mode or fraction mode, with configuration registers in the sys
syscon. So the PLLs node should be a child of SYS-SYSCON node. The formula for calculating
frequency is Fvco = Fref * (NI + NF) / M / Q1

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/starfive,jh7110-pll.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `starfive,jh7110-pll`.
- Required properties: `compatible`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `starfive,jh7110-pll`); `clocks` (max 1 items; Main Oscillator (24 MHz)); `#clock-cells` (const `1`; See <dt-bindings/clock/starfive,jh7110-crg.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/starfive,jh7110-pll.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `clocks`, `#clock-cells`
should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-pll.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-pll.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller {; compatible = "starfive,jh7110-pll";; clocks = <&osc>;; #clock-cells = <1>;; };

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-pll.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-stgcrg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-stgcrg.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
StarFive JH7110 System-Top-Group Clock and Reset Generator. It lives under `clock` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The file does not carry a long description, so its role is inferred from title,
path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/starfive,jh7110-stgcrg.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `starfive,jh7110-stgcrg`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `starfive,jh7110-stgcrg`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/starfive,jh7110-crg.h> for valid indices.); `#reset-cells` (const `1`; See <dt-bindings/reset/starfive,jh7110-crg.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/starfive,jh7110-crg.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#clock-cells`, `#reset-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-stgcrg.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-stgcrg.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/starfive,jh7110-crg.h>; stgcrg: clock-controller@10230000 {; compatible = "starfive,jh7110-stgcrg";; reg = <0x10230000 0x10000>;; clocks = <&osc>,

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-stgcrg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-syscrg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-syscrg.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
StarFive JH7110 System Clock and Reset Generator. It lives under `clock` bindings and gives dt-
schema a machine-readable contract for matching hardware nodes before those nodes reach kernel
drivers. The file does not carry a long description, so its role is inferred from title, path,
and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/starfive,jh7110-syscrg.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `starfive,jh7110-syscrg`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `starfive,jh7110-syscrg`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/starfive,jh7110-crg.h> for valid indices.); `#reset-cells` (const `1`; See <dt-bindings/reset/starfive,jh7110-crg.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 2 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/starfive,jh7110-syscrg.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#clock-cells`, `#reset-cells` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-syscrg.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-syscrg.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@13020000 {; compatible = "starfive,jh7110-syscrg";; reg = <0x13020000 0x10000>;; clocks = <&osc>, <&gmac1_rmii_refin>,; <&gmac1_rgmii_rxin>,

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-syscrg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-voutcrg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-voutcrg.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
StarFive JH7110 Video-Output Clock and Reset Generator. It lives under `clock` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The file does not carry a long description, so its role is inferred from title,
path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/starfive,jh7110-voutcrg.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `starfive,jh7110-voutcrg`.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `#clock-cells`, `#reset-cells`, `power-domains`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `resets`, `power-domains`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `starfive,jh7110-voutcrg`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/starfive,jh7110-crg.h> for valid indices.); `resets` (max 1 items; Vout Top core); `power-domains` (max 1 items; Vout domain power); `#reset-cells` (const `1`; See <dt-bindings/reset/starfive,jh7110-crg.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/starfive,jh7110-crg.h`, `dt-bindings/power/starfive,jh7110-pmu.h`, `dt-bindings/reset/starfive,jh7110-crg.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `resets`, `#clock-cells`, `#reset-cells`, `power-domains` should be caught by dt-schema
before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-voutcrg.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-voutcrg.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/starfive,jh7110-crg.h>; #include <dt-bindings/power/starfive,jh7110-pmu.h>; #include <dt-bindings/reset/starfive,jh7110-crg.h>; voutcrg: clock-controller@295C0000 {; compatible = "starfive,...

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/starfive,jh7110-voutcrg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/stericsson,u8500-clks.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/stericsson,u8500-clks.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
ST-Ericsson DB8500 (U8500) clocks. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: While named "U8500 clocks" these clocks are inside the DB8500 digital
baseband system-on-chip and its siblings such as DB8520. These bindings consider the clocks
present in the SoC itself, not off-chip clocks. There are four different on-chip clocks - RTC
(32 kHz), CPU clock (SMP TWD), PRCMU (power reset and control management unit) clocks and PRCC
(peripheral reset and clock controller) clocks. For some reason PRCC 4 does not exist so the
itemization can be a bit unintuitive.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/stericsson,u8500-clks.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `stericsson,u8500-clks`, `stericsson,u8540-clks`, `stericsson,u9540-clks`.
- Required properties: `compatible`, `reg`, `prcmu-clock`, `prcc-periph-clock`, `prcc-kernel-clock`, `rtc32k-clock`, `smp-twd-clock`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `prcmu-clock`, `prcc-periph-clock`, `prcc-kernel-clock`, `prcc-reset-controller`, `rtc32k-clock`, `smp-twd-clock`, `clkout-clock`.
- Child-node or pattern API: `prcmu-clock` object; `prcc-periph-clock` object; `prcc-kernel-clock` object; `prcc-reset-controller` object; `rtc32k-clock` object; `smp-twd-clock` object; `clkout-clock` object.
- Property detail signals: `compatible` (enum `stericsson,u8500-clks`, `stericsson,u8540-clks`, `stericsson,u9540-clks`); `prcmu-clock` (type `object`; A subnode with one clock cell for PRCMU (power, reset, control management unit) clocks. The cell indicates which PRCM...); `prcc-periph-clock` (type `object`; A subnode with two clock cells for PRCC (peripheral reset and clock controller) peripheral clocks. The first cell ind...); `prcc-kernel-clock` (type `object`; A subnode with two clock cells for PRCC (peripheral reset and clock controller) kernel clocks. The first cell indicat...); `prcc-reset-controller` (type `object`; A subnode with two reset cells for the reset portions of the PRCC (peripheral reset and clock controller). The first...); `rtc32k-clock` (type `object`; A subnode with zero clock cells for the 32kHz RTC clock.); `smp-twd-clock` (type `object`; A subnode for the ARM SMP Timer Watchdog cluster with zero clock cells.); `clkout-clock` (type `object`; A subnode with three clock cells for externally routed clocks, output clocks. These are two PRCMU-internal clocks tha...).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/ste-db8500-clkout.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `prcmu-clock`,
`prcc-periph-clock`, `prcc-kernel-clock`, `rtc32k-clock`, `smp-twd-clock` should be caught by
dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/stericsson,u8500-clks.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/stericsson,u8500-clks.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/ste-db8500-clkout.h>; clocks@8012 {; compatible = "stericsson,u8500-clks";; reg = <0x8012f000 0x1000>, <0x8011f000 0x1000>,; <0x8000f000 0x1000>, <0xa03ff000 0x1000>,

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/stericsson,u8500-clks.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sunplus,sp7021-clkc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sunplus,sp7021-clkc.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Sunplus SP7021 SoC Clock Controller. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The file does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sunplus,sp7021-clkc.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sunplus,sp7021-clkc`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `sunplus,sp7021-clkc`); `reg` (max 3 items); `clocks` (max 1 items); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/sunplus,sp7021-clkc.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sunplus,sp7021-clkc.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sunplus,sp7021-clkc.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: extclk: osc0 {; compatible = "fixed-clock";; #clock-cells = <0>;; clock-frequency = <27000000>;; clock-output-names = "extclk";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sunplus,sp7021-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tenstorrent,atlantis-prcm-rcpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tenstorrent,atlantis-prcm-rcpu.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Tenstorrent Atlantis PRCM (Power, Reset, Clock Management) Module. It lives under `clock`
bindings and gives dt-schema a machine-readable contract for matching hardware nodes before
those nodes reach kernel drivers. The description says: Multifunctional register block found in
Tenstorrent Atlantis SoC whose main function is to control clocks and resets. This block is
instantiated multiple times in the SoC, each block controls clock and resets for a different
subsystem. RCPU prcm serves low speed IO interfaces.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/tenstorrent,atlantis-prcm-rcpu.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `tenstorrent,atlantis-prcm-rcpu`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `#reset-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `tenstorrent,atlantis-prcm-rcpu`); `reg` (max 1 items); `clocks` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/tenstorrent,atlantis-prcm-rcpu.h> for valid indices.); `#reset-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/tenstorrent,atlantis-prcm-rcpu.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells`, `#reset-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tenstorrent,atlantis-prcm-rcpu.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tenstorrent,atlantis-prcm-rcpu.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@a8000000 {; compatible = "tenstorrent,atlantis-prcm-rcpu";; reg = <0xa8000000 0x10000>;; clocks = <&osc_24m>;; #clock-cells = <1>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tenstorrent,atlantis-prcm-rcpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tesla,fsd-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tesla,fsd-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Tesla FSD (Full Self-Driving) SoC clock controller. It lives under `clock` bindings and gives
dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: FSD clock controller consist of several clock management
unit (CMU), which generates clocks for various internal SoC blocks. The root clock comes from
external OSC clock (24 MHz). All available clocks are defined as preprocessor macros in 'dt-
bindings/clock/fsd-clk.h' header.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/tesla,fsd-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `tesla,fsd-clock-cmu`, `tesla,fsd-clock-imem`, `tesla,fsd-clock-peric`, `tesla,fsd-clock-fsys0`, `tesla,fsd-clock-fsys1`, `tesla,fsd-clock-mfc`, `tesla,fsd-clock-cam_csi`.
- Required properties: `compatible`, `#clock-cells`, `clocks`, `clock-names`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `tesla,fsd-clock-cmu`, `tesla,fsd-clock-imem`, `tesla,fsd-clock-peric`, `tesla,fsd-clock-fsys0`, `tesla,fsd-clock-fsys1`, `tesla,fsd-clock-mfc`, `tesla,fsd-clock-cam_csi`); `reg` (max 1 items); `clocks` (1-6 items); `clock-names` (1-6 items); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 0 `oneOf`, 0 `anyOf`, and 7 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/fsd-clk.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `clocks`,
`clock-names`, `reg` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tesla,fsd-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tesla,fsd-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/fsd-clk.h>; clock_fsys1: clock-controller@16810000 {; compatible = "tesla,fsd-clock-fsys1";; reg = <0x16810000 0x3000>;; #clock-cells = <1>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/tesla,fsd-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/thead,th1520-clk-ap.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/thead,th1520-clk-ap.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
T-HEAD TH1520 AP sub-system clock controller. It lives under `clock` bindings and gives dt-
schema a machine-readable contract for matching hardware nodes before those nodes reach kernel
drivers. The description says: The T-HEAD TH1520 AP sub-system clock controller configures the
CPU, DPU, GMAC and TEE PLLs. Additionally the VO subsystem configures the clock gates for the
HDMI, MIPI and the GPU. SoC reference manual https://openbeagle.org/beaglev-ahead/beaglev-
ahead/-/blob/main/docs/TH1520%20System%20User%20Manual.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/thead,th1520-clk-ap.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `thead,th1520-clk-ap`, `thead,th1520-clk-vo`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `thead,th1520-clk-ap`, `thead,th1520-clk-vo`); `reg` (max 1 items); `#clock-cells` (const `1`; See <dt-bindings/clock/thead,th1520-clk-ap.h> for valid indices.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/thead,th1520-clk-ap.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/thead,th1520-clk-ap.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/thead,th1520-clk-ap.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/thead,th1520-clk-ap.h>; clock-controller@ef010000 {; compatible = "thead,th1520-clk-ap";; reg = <0xef010000 0x1000>;; clocks = <&osc>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/thead,th1520-clk-ap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am62-audio-refclk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am62-audio-refclk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding: TI
Audio Reference Clock. It lives under `clock` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The file does not
carry a long description, so its role is inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti,am62-audio-refclk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,am62-audio-refclk`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `clocks`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `clocks` (max 1 items); `#clock-cells` (const `0`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/ti,am62-audio-refclk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`clocks` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am62-audio-refclk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am62-audio-refclk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: audio_refclk0: clock@82e0 {; compatible = "ti,am62-audio-refclk";; reg = <0x82e0 0x4>;; clocks = <&k3_clks 157 0>;; assigned-clocks = <&k3_clks 157 0>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am62-audio-refclk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am654-ehrpwm-tbclk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am654-ehrpwm-tbclk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding: TI
EHRPWM Time Base Clock. It lives under `clock` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The file does not
carry a long description, so its role is inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti,am654-ehrpwm-tbclk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,am654-ehrpwm-tbclk`, `ti,am64-epwm-tbclk`, `ti,am62-epwm-tbclk`.
- Required properties: `compatible`, `#clock-cells`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/ti,am654-ehrpwm-tbclk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `reg`
should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am654-ehrpwm-tbclk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am654-ehrpwm-tbclk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: ehrpwm_tbclk: clock@4140 {; compatible = "ti,am654-ehrpwm-tbclk";; reg = <0x4140 0x18>;; #clock-cells = <1>;; };

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,am654-ehrpwm-tbclk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,cdce925.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,cdce925.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding: TI
CDCE913/925/937/949 programmable I2C clock synthesizers. It lives under `clock` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: Flexible Low Power LVCMOS Clock Generator with SSC Support
for EMI Reduction - CDCE(L)913: 1-PLL, 3 Outputs https://www.ti.com/product/cdce913 -
CDCE(L)925: 2-PLL, 5 Outputs https://www.ti.com/product/cdce925 - CDCE(L)937: 3-PLL, 7 Outputs
https://www.ti.com/product/cdce937 - CDCE(L)949: 4-PLL, 9 Outputs
https://www.ti.com/product/cdce949

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti,cdce925.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,cdce913`, `ti,cdce925`, `ti,cdce937`, `ti,cdce949`.
- Required properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `vdd-supply`, `vddout-supply`, `xtal-load-pf`.
- Child-node or pattern API: `^PLL[1-4]$`.
- Property detail signals: `compatible` (enum `ti,cdce913`, `ti,cdce925`, `ti,cdce937`, `ti,cdce949`); `reg` (max 1 items); `#clock-cells` (const `1`); `vdd-supply` (Regulator that provides 1.8V Vdd power supply); `vddout-supply` (Regulator that provides Vddout power supply. non-L variant: 2.5V or 3.3V for L variant: 1.8V for); `xtal-load-pf` (ref `/schemas/types.yaml#/definitions/uint32`; Crystal load-capacitor value to fine-tune performance on a board, or to compensate for external influences.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti,cdce925.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `#clock-
cells` should be caught by dt-schema before runtime.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,cdce925.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,cdce925.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: i2c {; #address-cells = <1>;; #size-cells = <0>;; cdce925: clock-controller@64 {; compatible = "ti,cdce925";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,cdce925.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,clkctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,clkctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments clkctrl clock. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: Texas Instruments SoCs can have a clkctrl clock controller for each
interconnect target module. The clkctrl clock controller manages functional and interface clocks
for each module. Each clkctrl controller can also gate one or more optional functional clocks
for a module, and can have one or more clock muxes. There is a clkctrl clock controller
typically for each interconnect target module on omap4 and later variants. The clock consumers
can specify the index of the clkctrl clock using the hardware offset from the clkctrl instance
register space. The optional clocks can be specified by clkctr...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti,clkctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,clkctrl`, `ti,clkctrl-l4-cfg`, `ti,clkctrl-l4-per`, `ti,clkctrl-l4-secure`, `ti,clkctrl-l4-wkup`.
- Required properties: `compatible`, `#clock-cells`, `clock-output-names`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,clkctrl`, `ti,clkctrl-l4-cfg`, `ti,clkctrl-l4-per`, `ti,clkctrl-l4-secure`, `ti,clkctrl-l4-wkup`); `reg` (1-8 items); `#clock-cells` (const `2`); `clock-output-names` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/ti,clkctrl.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `clock-
output-names`, `reg` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,clkctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,clkctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <1>;; clock@20 {; compatible = "ti,clkctrl";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,clkctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,lmk04832.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,lmk04832.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments LMK04832 Clock Controller. It lives under `clock` bindings and gives dt-schema
a machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: Devicetree binding for the LMK04832, a clock conditioner with JEDEC
JESD204B support. The LMK04832 is pin compatible with the LMK0482x family. Link to datasheet,
https://www.ti.com/lit/ds/symlink/lmk04832.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti,lmk04832.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,lmk04832`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: `ti,spi-4wire-rdbk`, `ti,vco-hz`, `ti,sysref-ddly`, `ti,sysref-mux`, `ti,sync-mode`, `ti,sysref-pulse-count`.
- Other declared properties: `spi-max-frequency`, `reset-gpios`.
- Child-node or pattern API: `@[0-9a-d]+$` requiring `reg`.
- Property detail signals: `compatible` (enum `ti,lmk04832`); `reg` (max 1 items); `#clock-cells` (const `1`); `#address-cells` (const `1`); `#size-cells` (const `0`); `ti,spi-4wire-rdbk` (enum `0`, `1`, `2`; ref `/schemas/types.yaml#/definitions/uint32`; Select SPI 4wire readback pin configuration. Available readback pins are, CLKin_SEL0 0 CLKin_SEL1 1 RESET 2); `ti,vco-hz` (Optional to set VCO frequency of the PLL in Hertz.); `ti,sysref-ddly` (ref `/schemas/types.yaml#/definitions/uint32`; SYSREF digital delay value.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti,lmk04832.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`clocks`, `clock-names` should be caught by dt-schema before runtime.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,lmk04832.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,lmk04832.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clocks {; lmk04832_oscin: oscin {; compatible = "fixed-clock";; #clock-cells = <0>;; clock-frequency = <122880000>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,lmk04832.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,sci-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,sci-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
TI-SCI clock controller. It lives under `clock` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The description
says: Some TI SoCs contain a system controller (like the Power Management Micro Controller
(PMMC) on Keystone 66AK2G SoC) that are responsible for controlling the state of the various
hardware modules present on the SoC. Communication between the host processor running an OS and
the system controller happens through a protocol called TI System Control Interface (TI-SCI
protocol). This clock controller node uses the TI SCI protocol to perform various clock
management of various hardware modules (devices) present on the SoC. This node must be a child
node of the associated TI-SCI system controller node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti,sci-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,k2g-sci-clk`.
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: `compatible`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `$nodename`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `ti,k2g-sci-clk`); `#clock-cells` (const `2`; The two cells represent values that the TI-SCI controller defines. The first cell should contain the device ID. The s...).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/ti,sci-clk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,sci-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,sci-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: k3_clks: clock-controller {; compatible = "ti,k2g-sci-clk";; #clock-cells = <2>;; };

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,sci-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,autoidle.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,autoidle.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding: TI
autoidle clock. It lives under `clock` bindings and gives dt-schema a machine-readable contract
for matching hardware nodes before those nodes reach kernel drivers. The description says: Some
clocks in TI SoC support the autoidle feature. These properties are applicable only if the clock
supports autoidle feature. It assumes a register mapped clock which can be put to idle
automatically by hardware based on usage and configuration bit setting. Autoidle clock is never
an individual clock, it is always a derivative of some basic clock like a gate, divider, or
fixed-factor.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,autoidle.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: No explicit compatible string was extracted from the parsed `compatible` schema; consumers rely on the surrounding schema constraints..
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: No standard framework property from the clock/interrupt/reset/regulator shortlist is declared at top level..
- Vendor or device-specific extensions: `ti,autoidle-shift`, `ti,invert-autoidle-bit`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `ti,autoidle-shift` (ref `/schemas/types.yaml#/definitions/uint32`; bit shift of the autoidle enable bit for the clock); `ti,invert-autoidle-bit` (type `boolean`; autoidle is enabled by setting the bit to 0).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. The top-level schema leaves extra properties
open with `additionalProperties: true`.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,autoidle.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- Because the top-level closure is not explicitly false, review should ensure common schemas still
prevent accidental typo properties from being accepted.
- There is no inline example, reducing regression coverage for real DTS shape changes in binding
checks.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,autoidle.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,autoidle.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: No inline DTS example is present.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,autoidle.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,clksel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,clksel.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding: TI
clksel clock. It lives under `clock` bindings and gives dt-schema a machine-readable contract
for matching hardware nodes before those nodes reach kernel drivers. The description says: The
TI CLKSEL clocks consist of consist of input clock mux bits, and in some cases also has divider,
multiplier and gate bits.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,clksel.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,clksel`.
- Required properties: `compatible`, `reg`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `#clock-cells`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `ranges`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `ti,clksel`); `reg` (max 1 items; The CLKSEL register range); `#clock-cells` (const `2`; The CLKSEL register and bit offset); `#address-cells` (enum `0`, `1`, `2`); `#size-cells` (enum `0`, `1`, `2`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. The accepted-property boundary is inherited
from referenced/common schema behavior or nested subschemas.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: No `$ref` dependencies were found in the parsed schema..
- Textual schema references: `/schemas/clock/ti/ti,clksel.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`
should be caught by dt-schema before runtime.
- Because the top-level closure is not explicitly false, review should ensure common schemas still
prevent accidental typo properties from being accepted.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,clksel.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,clksel.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clksel_gfx_fclk: clock@52c {; compatible = "ti,clksel";; reg = <0x25c 0x4>;; #clock-cells = <2>;; };

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,clksel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,composite-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,composite-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments composite clock. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: *Deprecated design pattern: one node per clock* This binding assumes a
register-mapped composite clock with multiple different sub-types: a multiplexer clock with
multiple input clock signals or parents, one of which can be selected as output, this behaves
exactly as [1]. an adjustable clock rate divider, this behaves exactly as [2]. a gating function
which can be used to enable and disable the output clock, this behaves exactly as [3]. The
binding must provide a list of the component clocks that shall be merged to this clock. The
component clocks shall be of one of the "ti,*composite*-cloc...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,composite-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,composite-clock`.
- Required properties: `compatible`, `#clock-cells`, `clocks`.
- Top-level framework properties: `compatible`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `ti,composite-clock`); `#clock-cells` (const `0`); `clock-output-names` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/ti/ti,composite-clock.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `clocks`
should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,composite-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,composite-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <0>;; usb_l4_gate_ick: clock-controller@a10 {; #clock-cells = <0>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,composite-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,divider-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,divider-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments divider clock. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: This clock It assumes a register-mapped adjustable clock rate divider that
does not gate and has only one input clock or parent. By default the value programmed into the
register is one less than the actual divisor value. E.g: register value actual divisor value 0 1
1 2 2 3 This assumption may be modified by the following optional properties: ti,index-starts-
at-one - valid divisor values start at 1, not the default of 0. E.g: register value actual
divisor value 1 1 2 2 3 3 ti,index-power-of-two - valid divisor values are powers of two. E.g:
register value actual divisor value 0 1 1 2 2 4 Addi...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,divider-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,divider-clock`, `ti,composite-divider-clock`.
- Required properties: `compatible`, `#clock-cells`, `clocks`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,dividers`, `ti,bit-shift`, `ti,min-div`, `ti,max-div`, `ti,index-starts-at-one`, `ti,index-power-of-two`, `ti,set-rate-parent`, `ti,latch-bit`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,divider-clock`, `ti,composite-divider-clock`); `reg` (max 1 items); `clocks` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,dividers` (ref `/schemas/types.yaml#/definitions/uint32-array`; array of integers defining divisors); `ti,bit-shift` (ref `/schemas/types.yaml#/definitions/uint32`; number of bits to shift the divider value); `ti,min-div` (ref `/schemas/types.yaml#/definitions/uint32`; min divisor for dividing the input clock rate, only needed if the first divisor is offset from the default value (1)).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. `unevaluatedProperties: false` closes the
node after referenced schemas and conditional branches are evaluated.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `ti,autoidle.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,divider-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `clocks`,
`reg` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,divider-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,divider-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <0>;; clock-controller@190 {; #clock-cells = <0>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,divider-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,fixed-factor-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,fixed-factor-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding: TI
fixed factor rate clock sources. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: This consists of a divider and a multiplier used to generate a fixed rate
clock. This also uses the autoidle support from TI autoidle clock.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,fixed-factor-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,fixed-factor-clock`.
- Required properties: `compatible`, `clocks`, `#clock-cells`, `ti,clock-mult`, `ti,clock-div`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,clock-div`, `ti,clock-mult`, `ti,set-rate-parent`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `ti,fixed-factor-clock`); `reg` (max 1 items); `clocks` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,clock-div` (ref `/schemas/types.yaml#/definitions/uint32`; Fixed divider); `ti,clock-mult` (ref `/schemas/types.yaml#/definitions/uint32`; Fixed multiplier); `ti,set-rate-parent` (type `boolean`; Propagate to parent clock).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. `unevaluatedProperties: false` closes the
node after referenced schemas and conditional branches are evaluated.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `ti,autoidle.yaml#`, `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,fixed-factor-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `clocks`, `#clock-cells`,
`ti,clock-mult`, `ti,clock-div` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,fixed-factor-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,fixed-factor-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus{; #address-cells = <1>;; #size-cells = <0>;; clock@1b4 {; compatible = "ti,fixed-factor-clock";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,fixed-factor-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,gate-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,gate-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments gate clock. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: *Deprecated design pattern: one node per clock* This clock is quite much
similar to the basic gate-clock [1], however, it supports a number of additional features. If no
register is provided for this clock, the code assumes that a clockdomain will be controlled
instead and the corresponding hw-ops for that is used. [1]
Documentation/devicetree/bindings/clock/gpio-gate-clock.yaml [2]
Documentation/devicetree/bindings/clock/ti/clockdomain.txt

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,gate-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,gate-clock`, `ti,wait-gate-clock`, `ti,dss-gate-clock`, `ti,am35xx-gate-clock`, `ti,clkdm-gate-clock`, `ti,hsdiv-gate-clock`, `ti,composite-gate-clock`, `ti,composite-no-wait-gate-clock`.
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,bit-shift`, `ti,set-bit-to-disable`, `ti,set-rate-parent`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,gate-clock`, `ti,wait-gate-clock`, `ti,dss-gate-clock`, `ti,am35xx-gate-clock`, `ti,clkdm-gate-clock`, `ti,hsdiv-gate-clock`, `ti,composite-gate-clock`, `ti,composite-no-wait-gate-clock`); `reg` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,bit-shift` (ref `/schemas/types.yaml#/definitions/uint32`; Number of bits to shift the bit-mask); `ti,set-bit-to-disable` (type `boolean`; Inverts default gate programming. Setting the bit gates the clock and clearing the bit ungates the clock.); `ti,set-rate-parent` (type `boolean`; clk_set_rate is propagated to parent clock,).

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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,gate-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,gate-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 2 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,gate-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <0>;; clock-controller@a00 {; #clock-cells = <0>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,gate-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,interface-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,interface-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments interface clock.. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: This clock is quite much similar to the basic gate-clock[1], however, it
supports a number of additional features, including companion clock finding (match corresponding
functional gate clock) and hardware autoidle enable / disable. [1]
Documentation/devicetree/bindings/clock/gpio-gate-clock.yaml

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,interface-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,omap3-interface-clock`, `ti,omap3-no-wait-interface-clock`, `ti,omap3-hsotgusb-interface-clock`, `ti,omap3-dss-interface-clock`, `ti,omap3-ssi-interface-clock`, `ti,am35xx-interface-clock`, `ti,omap2430-interface-clock`.
- Required properties: `compatible`, `clocks`, `#clock-cells`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,bit-shift`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,omap3-interface-clock`, `ti,omap3-no-wait-interface-clock`, `ti,omap3-hsotgusb-interface-clock`, `ti,omap3-dss-interface-clock`, `ti,omap3-ssi-interface-clock`, `ti,am35xx-interface-clock`, `ti,omap2430-interface-clock`); `reg` (max 1 items); `clocks` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,bit-shift` (ref `/schemas/types.yaml#/definitions/uint32`; bit shift for the bit enabling/disabling the clock).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,interface-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `clocks`, `#clock-cells`,
`reg` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,interface-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,interface-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <0>;; aes1_ick: clock-controller@3 {; #clock-cells = <0>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,interface-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,mux-clock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,mux-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments mux clock. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: This clock assumes a register-mapped multiplexer with multiple inpt clock
signals or parents, one of which can be selected as output. This clock does not gate or adjust
the parent rate via a divider or multiplier. By default the "clocks" property lists the parents
in the same order as they are programmed into the register. E.g: clocks = <&foo_clock>,
<&bar_clock>, <&baz_clock>; Results in programming the register as follows: register value
selected parent clock 0 foo_clock 1 bar_clock 2 baz_clock Some clock controller IPs do not allow
a value of zero to be programmed into the register, instead in...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,mux-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,mux-clock`, `ti,composite-mux-clock`.
- Required properties: `compatible`, `#clock-cells`, `clocks`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,bit-shift`, `ti,index-starts-at-one`, `ti,set-rate-parent`, `ti,latch-bit`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,mux-clock`, `ti,composite-mux-clock`); `reg` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,bit-shift` (ref `/schemas/types.yaml#/definitions/uint32`; Number of bits to shift the bit-mask); `ti,index-starts-at-one` (type `boolean`; Valid input select programming starts at 1, not zero); `ti,set-rate-parent` (type `boolean`; clk_set_rate is propagated to parent clock, not supported by the composite-mux-clock subtype.); `ti,latch-bit` (ref `/schemas/types.yaml#/definitions/uint32`; Latch the mux value to HW, only needed if the register access requires this. As an example, dra7x DPLL_GMAC H14 muxin...).

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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,mux-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `clocks`,
`reg` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,mux-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,mux-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <0>;; clock-controller@110 {; compatible = "ti,mux-clock";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,mux-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pipllct.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pipllct.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Toshiba Visconti5 TMPV770X PLL Controller. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: Toshia Visconti5 PLL controller which supports the PLLs on TMPV770X.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/toshiba,tmpv770x-pipllct.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `toshiba,tmpv7708-pipllct`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `clocks`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `toshiba,tmpv7708-pipllct`); `reg` (max 1 items); `clocks` (max 1 items; External reference clock (OSC2)); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/toshiba,tmpv770x-pipllct.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`clocks` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pipllct.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pipllct.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: osc2_clk: osc2-clk {; compatible = "fixed-clock";; clock-frequency = <20000000>;; #clock-cells = <0>;; };

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pipllct.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pismu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pismu.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Toshiba Visconti5 TMPV770x SMU controller. It lives under `clock` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: Toshia Visconti5 SMU (System Management Unit) which supports the clock and
resets on TMPV770x.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/toshiba,tmpv770x-pismu.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `toshiba,tmpv7708-pismu`, `syscon`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `#reset-cells`.
- Top-level framework properties: `compatible`, `reg`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#reset-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `#clock-cells` (const `1`); `#reset-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/toshiba,tmpv770x-pismu.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`#reset-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pismu.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pismu.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: soc {; #address-cells = <2>;; #size-cells = <2>;; pismu: syscon@24200000 {; compatible = "toshiba,tmpv7708-pismu", "syscon";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/toshiba,tmpv770x-pismu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,clocking-wizard.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,clocking-wizard.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Xilinx clocking wizard. It lives under `clock` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The description
says: The clocking wizard is a soft ip clocking block of Xilinx versal. It reads required input
clock frequencies from the devicetree and acts as clock clock output.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/xlnx,clocking-wizard.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `xlnx,clocking-wizard`, `xlnx,clocking-wizard-v5.2`, `xlnx,clocking-wizard-v6.0`, `xlnx,versal-clk-wizard`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `clocks`, `clock-names`, `xlnx,speed-grade`, `xlnx,nr-outputs`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: `xlnx,static-config`, `xlnx,speed-grade`, `xlnx,nr-outputs`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `xlnx,clocking-wizard`, `xlnx,clocking-wizard-v5.2`, `xlnx,clocking-wizard-v6.0`, `xlnx,versal-clk-wizard`); `reg` (max 1 items); `#clock-cells` (const `1`); `xlnx,static-config` (ref `/schemas/types.yaml#/definitions/flag`; Indicate whether the core has been configured without support for dynamic runtime reconfguration of the clocking prim...); `xlnx,speed-grade` (enum `1`, `2`, `3`; ref `/schemas/types.yaml#/definitions/uint32`; Speed grade of the device. Higher the speed grade faster is the FPGA device.); `xlnx,nr-outputs` (ref `/schemas/types.yaml#/definitions/uint32`; Number of outputs.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/xlnx,clocking-wizard.yaml`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`clocks`, `clock-names`, `xlnx,speed-grade`, `xlnx,nr-outputs` should be caught by dt-schema
before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,clocking-wizard.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,clocking-wizard.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: clock-controller@b0000000 {; compatible = "xlnx,clocking-wizard";; reg = <0xb0000000 0x10000>;; #clock-cells = <1>;; xlnx,static-config;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,clocking-wizard.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,vcu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,vcu.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
LogicoreIP designed compatible with Xilinx ZYNQ family.. It lives under `clock` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: LogicoreIP design to provide the isolation between
processing system and programmable logic. Also provides the list of register set to configure
the frequency.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/xlnx,vcu.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `xlnx,vcu`, `xlnx,vcu-logicoreip-1.0`.
- Required properties: `reg`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `reset-gpios`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `reset-gpios` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/gpio/gpio.h`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `reg`, `clocks`, `clock-names` should be
caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,vcu.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,vcu.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/gpio/gpio.h>; fpga {; #address-cells = <2>;; #size-cells = <2>;; xlnx_vcu: vcu@a0040000 {

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,vcu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,versal-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,versal-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Xilinx Versal clock controller. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: The clock controller is a hardware block of Xilinx versal clock tree. It reads
required input clock frequencies from the devicetree and acts as clock provider for all clock
consumers of PS clocks.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/xlnx,versal-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `xlnx,versal-clk`, `xlnx,zynqmp-clk`, `xlnx,versal-net-clk`.
- Required properties: `compatible`, `#clock-cells`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `clocks` (2-8 items; List of clock specifiers which are external input clocks to the given clock controller.); `clock-names` (2-8 items); `#clock-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 1 `oneOf`, 0 `anyOf`, and 3 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/clock/xlnx,versal-clk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `clocks`,
`clock-names` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,versal-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,versal-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: firmware {; zynqmp_firmware: zynqmp-firmware {; compatible = "xlnx,zynqmp-firmware";; method = "smc";; versal_clk: clock-controller {

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/xlnx,versal-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/gocontroll,moduline-module-slot.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/gocontroll,moduline-module-slot.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a physical connector binding:
GOcontroll Moduline Module slot. It lives under `connector` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: The GOcontroll Moduline module slot represents a connector that fullfills
the Moduline slot specification, and can thus house any IO module that is also built to this
spec.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/connector/gocontroll,moduline-module-slot.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `gocontroll,moduline-module-slot`.
- Required properties: `compatible`, `reg`, `reset-gpios`, `interrupts`, `sync-gpios`, `i2c-bus`, `slot-number`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `reset-gpios`, `sync-gpios`, `vdd-supply`, `vddp-supply`, `vddhpp-supply`, `power-supply`, `i2c-bus`, `slot-number`, `spi-max-frequency`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `gocontroll,moduline-module-slot`); `reg` (max 1 items); `interrupts` (max 1 items; indicates readiness, high means busy.); `reset-gpios` (max 1 items; resets the module, active low.); `sync-gpios` (max 1 items; sync line between all module slots.); `vdd-supply` (low power 3v3 supply generally for the microcontroller.); `vddp-supply` (medium power 5v0 supply for on module low power peripherals.); `vddhpp-supply` (high power 6v-8v supply for on module high power peripherals.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`.
- Example/header integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/interrupt-controller/irq.h`.
Runtime integration is with connector, Type-C, PCIe M.2, module slot, and OF graph endpoint
consumers. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `reset-gpios`,
`interrupts`, `sync-gpios`, `i2c-bus`, `slot-number` should be caught by dt-schema before
runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/gocontroll,moduline-module-slot.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/gocontroll,moduline-module-slot.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/gpio/gpio.h>; #include <dt-bindings/interrupt-controller/irq.h>; spi {; #address-cells = <1>;; #size-cells = <0>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/gocontroll,moduline-module-slot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-e-connector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-e-connector.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a physical connector binding: PCIe M.2
Mechanical Key E Connector. It lives under `connector` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: A PCIe M.2 E connector node represents a physical PCIe M.2 Mechanical Key E
connector. Mechanical Key E connectors are used to connect Wireless Connectivity devices
including combinations of Wi-Fi, BT, NFC to the host machine over interfaces like PCIe/SDIO,
USB/UART+PCM, and I2C.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/connector/pcie-m2-e-connector.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `pcie-m2-e-connector`.
- Required properties: `compatible`, `vpcie3v3-supply`.
- Top-level framework properties: `compatible`, `clocks`, `ports`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `vpcie3v3-supply`, `vpcie1v8-supply`, `i2c-parent`, `w-disable1-gpios`, `w-disable2-gpios`, `viocfg-gpios`, `uart-wake-gpios`, `sdio-wake-gpios`, `sdio-reset-gpios`, `vendor-porta-gpios`, `vendor-portb-gpios`, `vendor-portc-gpios`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `pcie-m2-e-connector`); `clocks` (max 1 items; 32.768 KHz Suspend Clock (SUSCLK) input from the host system to the M.2 card. Refer, PCI Express M.2 Specification r4...); `ports` (ref `/schemas/graph.yaml#/properties/ports`; OF graph bindings modeling the interfaces exposed on the connector. Since a single connector can have multiple interf...); `vpcie3v3-supply` (A phandle to the regulator for 3.3v supply.); `vpcie1v8-supply` (A phandle to the regulator for VIO 1.8v supply.); `i2c-parent` (ref `/schemas/types.yaml#/definitions/phandle`; I2C interface); `w-disable1-gpios` (max 1 items; GPIO output to W_DISABLE1# signal. This signal is used by the host system to disable WiFi radio in the M.2 card. Refe...); `w-disable2-gpios` (max 1 items; GPIO output to W_DISABLE2# signal. This signal is used by the host system to disable BT radio in the M.2 card. Refer,...).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 3 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.
- Example/header integration: `dt-bindings/gpio/gpio.h`.
Runtime integration is with connector, Type-C, PCIe M.2, module slot, and OF graph endpoint
consumers. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `vpcie3v3-supply` should be
caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-e-connector.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-e-connector.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/gpio/gpio.h>; connector {; compatible = "pcie-m2-e-connector";; vpcie3v3-supply = <&vreg_wcn_3p3>;; vpcie1v8-supply = <&vreg_l15b_1p8>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-e-connector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-m-connector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-m-connector.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a physical connector binding: PCIe M.2
Mechanical Key M Connector. It lives under `connector` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: A PCIe M.2 M connector node represents a physical PCIe M.2 Mechanical Key M
connector. The Mechanical Key M connectors are used to connect SSDs to the host system over
PCIe/SATA interfaces. These connectors also offer optional interfaces like USB, SMBus.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/connector/pcie-m2-m-connector.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `pcie-m2-m-connector`.
- Required properties: `compatible`, `vpcie3v3-supply`.
- Top-level framework properties: `compatible`, `clocks`, `ports`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `vpcie3v3-supply`, `vpcie1v8-supply`, `i2c-parent`, `pedet-gpios`, `viocfg-gpios`, `pwrdis-gpios`, `pln-gpios`, `plas3-gpios`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `pcie-m2-m-connector`); `clocks` (max 1 items; 32.768 KHz Suspend Clock (SUSCLK) input from the host system to the M.2 card. Refer, PCI Express M.2 Specification r4...); `ports` (ref `/schemas/graph.yaml#/properties/ports`; OF graph bindings modeling the interfaces exposed on the connector. Since a single connector can have multiple interf...); `vpcie3v3-supply` (A phandle to the regulator for 3.3v supply.); `vpcie1v8-supply` (A phandle to the regulator for VIO 1.8v supply.); `i2c-parent` (ref `/schemas/types.yaml#/definitions/phandle`; I2C interface); `pedet-gpios` (max 1 items; GPIO input to PEDET signal. This signal is used by the host systems to determine the communication protocol that the...); `viocfg-gpios` (max 1 items; GPIO input to IO voltage configuration (VIO_CFG) signal. This signal is used by the host systems to determine whether...).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 1 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`.
- Example/header integration: `dt-bindings/gpio/gpio.h`.
Runtime integration is with connector, Type-C, PCIe M.2, module slot, and OF graph endpoint
consumers. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `vpcie3v3-supply` should be
caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-m-connector.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-m-connector.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/gpio/gpio.h>; connector {; compatible = "pcie-m2-m-connector";; vpcie3v3-supply = <&vreg_nvme>;; i2c-parent = <&i2c0>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/pcie-m2-m-connector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/usb-connector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/usb-connector.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a physical connector binding: USB
Connector. It lives under `connector` bindings and gives dt-schema a machine-readable contract
for matching hardware nodes before those nodes reach kernel drivers. The description says: A USB
connector node represents a physical USB connector. It should be a child of a USB interface
controller or a separate node when it is attached to both MUX and USB interface controller.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/connector/usb-connector.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `gpio-usb-b-connector`, `usb-b-connector`, `samsung,usb-connector-11pin`, `usb-a-connector`, `usb-c-connector`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`, `reg`, `ports`, `port`, `id-gpios`, `vbus-gpios`, `vbus-supply`, `data-role`, `power-role`, `try-power-role`, `typec-power-opmode`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `label`, `type`, `self-powered`, `pd-disable`, `sink-vdos`, `sink-vdos-v1`, `accessory-mode-audio`, `accessory-mode-debug`, `altmodes`, `new-source-frs-typec-current`, `slow-charger-loop`, `capabilities`, plus 9 more properties.
- Child-node or pattern API: `altmodes` object; `capabilities` object.
- Property detail signals: `reg` (max 1 items); `ports` (ref `/schemas/graph.yaml#/properties/ports`; OF graph bindings modeling any data bus to the connector unless the bus is between parent node and the connector. Sin...); `port` (ref `/schemas/graph.yaml#/properties/port`; OF graph bindings modeling a data bus to the connector, e.g. there is a single High Speed (HS) port present in this c...); `id-gpios` (max 1 items; An input gpio for USB ID pin.); `vbus-gpios` (max 1 items; An input gpio for USB VBus pin, used to detect presence of VBUS 5V.); `vbus-supply` (A phandle to the regulator for USB VBUS if needed when host mode or dual role mode is supported. Particularly, if use...); `data-role` (enum `host`, `device`, `dual`; ref `/schemas/types.yaml#/definitions/string`; Data role if Type C connector supports USB data. "dual" refers Dual Role Device (DRD).); `power-role` (enum `source`, `sink`, `dual`; ref `/schemas/types.yaml#/definitions/string`; Determines the power role that the Type C connector will support. "dual" refers to Dual Role Port (DRP).).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 1 `oneOf`, 2 `anyOf`, and 2 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. `unevaluatedProperties: false` closes the
node after referenced schemas and conditional branches are evaluated.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint16`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `#/$defs/capabilities`, `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint8`.
- Example/header integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/usb/pd.h`.
Runtime integration is with connector, Type-C, PCIe M.2, module slot, and OF graph endpoint
consumers. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible` should be caught by dt-
schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/usb-connector.yaml` to parse this YAML, validate meta-schema rules, and compile its 7 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/usb-connector.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: muic-max77843 {; usb_con1: connector {; compatible = "usb-b-connector";; label = "micro-USB";; type = "micro";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/connector/usb-connector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/fsl,ftm-quaddec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/fsl,ftm-quaddec.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a counter device binding: FlexTimer
Quadrature decoder counter. It lives under `counter` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: Exposes a simple counter for the quadrature decoder mode.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/counter/fsl,ftm-quaddec.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,ftm-quaddec`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `big-endian`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `fsl,ftm-quaddec`); `reg` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/counter/fsl,ftm-quaddec.yaml`.
Runtime integration is with Linux counter subsystem drivers, interrupt/GPIO providers, clocks,
and pin/control blocks. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg` should be caught by
dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/fsl,ftm-quaddec.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/fsl,ftm-quaddec.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: counter@29d0000 {; compatible = "fsl,ftm-quaddec";; reg = <0x29d0000 0x10000>;; big-endian;; };

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/fsl,ftm-quaddec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/interrupt-counter.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/interrupt-counter.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a counter device binding: Interrupt
counter. It lives under `counter` bindings and gives dt-schema a machine-readable contract for
matching hardware nodes before those nodes reach kernel drivers. The description says: A generic
interrupt counter to measure interrupt frequency. It was developed and used for agricultural
devices to measure rotation speed of wheels or other tools. Since the direction of rotation is
not important, only one signal line is needed. Interrupts or gpios are required. If both are
defined, the interrupt will take precedence for counting interrupts.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/counter/interrupt-counter.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `interrupt-counter`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`, `interrupts`, `gpios`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `interrupt-counter`); `interrupts` (max 1 items); `gpios` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 1 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/interrupt-controller/irq.h`.
Runtime integration is with Linux counter subsystem drivers, interrupt/GPIO providers, clocks,
and pin/control blocks. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible` should be caught by dt-
schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/interrupt-counter.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/interrupt-counter.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/gpio/gpio.h>; counter-0 {; compatible = "interrupt-counter";; interrupts-extended = <&gpio 0 IRQ_TYPE_EDGE_RISING>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/interrupt-counter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti,am62-ecap-capture.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti,am62-ecap-capture.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a counter device binding: Texas
Instruments Enhanced Capture (eCAP) Module. It lives under `counter` bindings and gives dt-
schema a machine-readable contract for matching hardware nodes before those nodes reach kernel
drivers. The description says: The eCAP module resources can be used to capture timestamps on
input signal events (falling/rising edges).

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/counter/ti,am62-ecap-capture.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,am62-ecap-capture`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `ti,am62-ecap-capture`); `reg` (max 1 items); `interrupts` (max 1 items); `clocks` (max 1 items); `clock-names` (const `fck`); `power-domains` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/soc/ti,sci_pm_domain.h`.
Runtime integration is with Linux counter subsystem drivers, interrupt/GPIO providers, clocks,
and pin/control blocks. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `clock-names` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti,am62-ecap-capture.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti,am62-ecap-capture.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/soc/ti,sci_pm_domain.h>; soc {; #address-cells = <2>;; #size-cells = <2>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti,am62-ecap-capture.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti-eqep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti-eqep.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a counter device binding: Texas
Instruments Enhanced Quadrature Encoder Pulse (eQEP) Module. It lives under `counter` bindings
and gives dt-schema a machine-readable contract for matching hardware nodes before those nodes
reach kernel drivers. The file does not carry a long description, so its role is inferred from
title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/counter/ti-eqep.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,am3352-eqep`, `ti,am62-eqep`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,am3352-eqep`, `ti,am62-eqep`); `reg` (max 1 items); `interrupts` (max 1 items; The eQEP event interrupt); `clocks` (max 1 items; The functional and interface clock that determines the clock rate for the eQEP peripheral.); `clock-names` (const `sysclkout`); `power-domains` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
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
- Textual schema references: `/schemas/counter/ti-eqep.yaml`.
Runtime integration is with Linux counter subsystem drivers, interrupt/GPIO providers, clocks,
and pin/control blocks. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti-eqep.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti-eqep.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: eqep0: counter@180 {; compatible = "ti,am3352-eqep";; reg = <0x180 0x80>;; clocks = <&l4ls_gclk>;; interrupts = <79>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti-eqep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpu/idle-states.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpu/idle-states.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU idle-state binding: Idle states.
It lives under `cpu` bindings and gives dt-schema a machine-readable contract for matching
hardware nodes before those nodes reach kernel drivers. The description says:
========================================== 1 - Introduction
========================================== ARM and RISC-V systems contain HW capable of managing
power consumption dynamically, where cores can be put in different low-power states (ranging
from simple wfi to power gating) according to OS PM policies. The CPU states representing the
range of dynamic idle states that a processor can enter at run-time, can be specified through
device tree bindings representing the parameters required to enter/exit specific idle states on
a given processor. ========================================== 2 - ARM idle states
================...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpu/idle-states.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: No explicit compatible string was extracted from the parsed `compatible` schema; consumers rely on the surrounding schema constraints..
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: No standard framework property from the clock/interrupt/reset/regulator shortlist is declared at top level..
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `$nodename`, `entry-method`.
- Child-node or pattern API: `^(cpu|cluster)-` requiring `compatible`, `entry-latency-us`, `exit-latency-us`, `min-residency-us`.
- Property detail signals: `$nodename` (const `idle-states`); `entry-method` (const `psci`; Usage and definition depend on ARM architecture version. On ARM v8 64-bit this property is required. On ARM 32-bit sy...).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/string`.
- Textual schema references: `/schemas/cpu/idle-states.yaml`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with CPU nodes through `cpu-idle-states`, PSCI/cpuidle drivers, and
scheduler/power-management validation. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpu/idle-states.yaml` to parse this YAML, validate meta-schema rules, and compile its 3 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpu/idle-states.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: cpus {; #size-cells = <0>;; #address-cells = <2>;; cpu@0 {; device_type = "cpu";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpu/idle-states.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/airoha,en7581-cpufreq.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/airoha,en7581-cpufreq.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding: Airoha
EN7581 CPUFreq. It lives under `cpufreq` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The description
says: On newer Airoha SoC, CPU Frequency is scaled indirectly with SMC commands to ATF. A
virtual clock is exposed. This virtual clock is a get-only clock and is used to expose the
current global CPU clock. The frequency info comes by the output of the SMC command that reports
the clock in MHz. The SMC sets the CPU clock by providing an index, this is modelled as
performance states in a power domain. CPUs can't be individually scaled as the CPU frequency is
shared across all CPUs and is global.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/airoha,en7581-cpufreq.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `airoha,en7581-cpufreq`.
- Required properties: `compatible`, `#clock-cells`, `#power-domain-cells`, `operating-points-v2`.
- Top-level framework properties: `compatible`, `#clock-cells`, `operating-points-v2`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#power-domain-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `airoha,en7581-cpufreq`); `#clock-cells` (const `0`); `#power-domain-cells` (const `0`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/cpufreq/airoha,en7581-cpufreq.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `#power-
domain-cells`, `operating-points-v2` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/airoha,en7581-cpufreq.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/airoha,en7581-cpufreq.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: performance-domain {; compatible = "airoha,en7581-cpufreq";; operating-points-v2 = <&cpu_smcc_opp_table>;; #power-domain-cells = <0>;; #clock-cells = <0>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/airoha,en7581-cpufreq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/apple,cluster-cpufreq.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/apple,cluster-cpufreq.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding: Apple
SoC cluster cpufreq device. It lives under `cpufreq` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: Apple SoCs (e.g. M1) have a per-cpu-cluster DVFS controller that is part of
the cluster management register block. This binding uses the standard operating-points-v2 table
to define the CPU performance states, with the opp-level property specifying the hardware
p-state index for that level.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/apple,cluster-cpufreq.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `apple,cluster-cpufreq`, `apple,t8103-cluster-cpufreq`, `apple,t7000-cluster-cpufreq`, `apple,s5l8960x-cluster-cpufreq`, `apple,t6020-cluster-cpufreq`, `apple,t8112-cluster-cpufreq`, `apple,s8000-cluster-cpufreq`, `apple,t8010-cluster-cpufreq`, `apple,t8015-cluster-cpufreq`, `apple,t6000-cluster-cpufreq`.
- Required properties: `compatible`, `reg`, `#performance-domain-cells`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#performance-domain-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `#performance-domain-cells` (const `0`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/cpufreq/apple,cluster-cpufreq.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#performance-
domain-cells` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/apple,cluster-cpufreq.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/apple,cluster-cpufreq.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: // This example shows a single CPU per domain and 2 domains,; // with two p-states per domain.; // Shipping hardware has 2-4 CPUs per domain and 2-6 domains.; cpus {; #address-cells = <2>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/apple,cluster-cpufreq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-mediatek-hw.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-mediatek-hw.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding:
MediaTek's CPUFREQ. It lives under `cpufreq` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The description
says: CPUFREQ HW is a hardware engine used by MediaTek SoCs to manage frequency in hardware. It
is capable of controlling frequency for multiple clusters.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/cpufreq-mediatek-hw.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `mediatek,cpufreq-hw`.
- Required properties: `compatible`, `reg`, `#performance-domain-cells`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#performance-domain-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `mediatek,cpufreq-hw`); `reg` (1-2 items; Addresses and sizes for the memory of the HW bases in each frequency domain. Each entry corresponds to a register ban...); `#performance-domain-cells` (const `1`; Number of cells in a performance domain specifier. Set const to 1 here for nodes providing multiple performance domains.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/cpufreq/cpufreq-mediatek-hw.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#performance-
domain-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-mediatek-hw.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-mediatek-hw.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: cpus {; #address-cells = <1>;; #size-cells = <0>;; cpu0: cpu@0 {; device_type = "cpu";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-mediatek-hw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-qcom-hw.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-qcom-hw.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding:
Qualcomm Technologies, Inc. CPUFREQ. It lives under `cpufreq` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: CPUFREQ HW is a hardware engine used by some Qualcomm Technologies, Inc.
(QTI) SoCs to manage frequency in hardware. It is capable of controlling frequency for multiple
clusters.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/cpufreq-qcom-hw.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `qcom,cpufreq-hw`, `qcom,cpufreq-epss`, `qcom,qcm2290-cpufreq-hw`, `qcom,qcs615-cpufreq-hw`, `qcom,sc7180-cpufreq-hw`, `qcom,sc8180x-cpufreq-hw`, `qcom,sdm670-cpufreq-hw`, `qcom,sdm845-cpufreq-hw`, `qcom,sm6115-cpufreq-hw`, `qcom,sm6350-cpufreq-hw`, `qcom,sm8150-cpufreq-hw`, `qcom,eliza-cpufreq-epss`, `qcom,milos-cpufreq-epss`, `qcom,qcs8300-cpufreq-epss`, plus 14 more.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#freq-domain-cells`.
- Top-level framework properties: `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#freq-domain-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (min 1 items); `reg-names` (min 1 items); `interrupts` (1-4 items); `interrupt-names` (min 1 items); `#clock-cells` (const `1`); `#freq-domain-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 1 `oneOf`, 0 `anyOf`, and 5 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/qcom,gcc-sdm845.h`, `dt-bindings/clock/qcom,rpmh.h`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#freq-domain-cells` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-qcom-hw.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-qcom-hw.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/qcom,gcc-sdm845.h>; #include <dt-bindings/clock/qcom,rpmh.h>; // Example 1: Dual-cluster, Quad-core per cluster. CPUs within a cluster; // switch DCVS state together.; cpus {

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-qcom-hw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/mediatek,mt8196-cpufreq-hw.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/mediatek,mt8196-cpufreq-hw.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding:
MediaTek Hybrid CPUFreq for MT8196/MT6991 series SoCs. It lives under `cpufreq` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: MT8196 uses CPUFreq management hardware that supports
dynamic voltage frequency scaling (dvfs), and can support several performance domains.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/mediatek,mt8196-cpufreq-hw.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `mediatek,mt8196-cpufreq-hw`.
- Required properties: `compatible`, `reg`, `#performance-domain-cells`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#performance-domain-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `mediatek,mt8196-cpufreq-hw`); `#performance-domain-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/cpufreq/mediatek,mt8196-cpufreq-hw.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#performance-
domain-cells` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/mediatek,mt8196-cpufreq-hw.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/mediatek,mt8196-cpufreq-hw.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: cpus {; #address-cells = <1>;; #size-cells = <0>;; cpu0: cpu@0 {; device_type = "cpu";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/mediatek,mt8196-cpufreq-hw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qcom-cpufreq-nvmem.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qcom-cpufreq-nvmem.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding:
Qualcomm Technologies, Inc. NVMEM CPUFreq. It lives under `cpufreq` bindings and gives dt-schema
a machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: In certain Qualcomm Technologies, Inc. SoCs such as QCS404, The CPU supply
voltage is dynamically configured by Core Power Reduction (CPR) depending on current CPU
frequency and efuse values. CPR provides a power domain with multiple levels that are selected
depending on the CPU OPP in use. The CPUFreq driver sets the CPR power domain level according to
the required OPPs defined in the CPU OPP tables. For old implementation efuses are parsed to
select the correct opp table and voltage and CPR is not supported/used.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/qcom-cpufreq-nvmem.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: No explicit compatible string was extracted from the parsed `compatible` schema; consumers rely on the surrounding schema constraints..
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: No standard framework property from the clock/interrupt/reset/regulator shortlist is declared at top level..
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: `^opp-table(-[a-z0-9]+)?$`.
- Property detail signals: The schema relies mostly on common references and required property presence rather than rich per-property local constraints..

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 2
`allOf`, 0 `oneOf`, 0 `anyOf`, and 4 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. The top-level schema leaves extra properties
open with `additionalProperties: true`.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `/schemas/opp/opp-v2-kryo-cpu.yaml#`, `/schemas/opp/opp-v2-qcom-level.yaml#`.
- Textual schema references: `/schemas/cpufreq/qcom-cpufreq-nvmem.yaml`, `/schemas/opp/opp-v2-kryo-cpu.yaml`, `/schemas/opp/opp-v2-qcom-level.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- Because the top-level closure is not explicitly false, review should ensure common schemas still
prevent accidental typo properties from being accepted.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qcom-cpufreq-nvmem.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qcom-cpufreq-nvmem.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: / {; model = "Qualcomm Technologies, Inc. QCS404 EVB 1000";; compatible = "qcom,qcs404-evb-1000", "qcom,qcs404-evb", "qcom,qcs404";; #address-cells = <2>;; #size-cells = <2>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qcom-cpufreq-nvmem.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qemu,virtual-cpufreq.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qemu,virtual-cpufreq.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding:
Virtual CPUFreq. It lives under `cpufreq` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The description
says: Virtual CPUFreq is a virtualized driver in guest kernels that sends performance selection
of its vCPUs as a hint to the host through MMIO regions. Each vCPU is associated with a
performance domain which can be shared with other vCPUs. Each performance domain has its own set
of registers for performance controls.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/qemu,virtual-cpufreq.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `qemu,virtual-cpufreq`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `qemu,virtual-cpufreq`); `reg` (max 1 items; Address and size of region containing performance controls for each of the performance domains. Regions for each perf...).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/cpufreq/qemu,virtual-cpufreq.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg` should be caught by
dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qemu,virtual-cpufreq.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qemu,virtual-cpufreq.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: soc {; #address-cells = <1>;; #size-cells = <1>;; cpufreq@1040000 {; compatible = "qemu,virtual-cpufreq";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qemu,virtual-cpufreq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun4i-a10-crypto.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun4i-a10-crypto.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Allwinner
A10 Security System. It lives under `crypto` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The file does not
carry a long description, so its role is inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/allwinner,sun4i-a10-crypto.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `allwinner,sun4i-a10-crypto`, `allwinner,sun5i-a13-crypto`, `allwinner,sun6i-a31-crypto`, `allwinner,sun7i-a20-crypto`, `allwinner,sun8i-a33-crypto`, `allwinner,sun8i-v3s-crypto`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `dmas`, `dma-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `interrupts` (max 1 items); `resets` (max 1 items); `reset-names` (const `ahb`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
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
- Schema references: No `$ref` dependencies were found in the parsed schema..
- Textual schema references: `/schemas/crypto/allwinner,sun4i-a10-crypto.yaml`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `clock-names` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun4i-a10-crypto.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun4i-a10-crypto.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: crypto: crypto-engine@1c15000 {; compatible = "allwinner,sun4i-a10-crypto";; reg = <0x01c15000 0x1000>;; interrupts = <86>;; clocks = <&ahb_gates 5>, <&ss_clk>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun4i-a10-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ce.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ce.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Allwinner
Crypto Engine driver. It lives under `crypto` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The file does not
carry a long description, so its role is inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/allwinner,sun8i-ce.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `allwinner,sun8i-h3-crypto`, `allwinner,sun8i-r40-crypto`, `allwinner,sun20i-d1-crypto`, `allwinner,sun50i-a64-crypto`, `allwinner,sun50i-h5-crypto`, `allwinner,sun50i-h6-crypto`, `allwinner,sun50i-h616-crypto`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `allwinner,sun8i-h3-crypto`, `allwinner,sun8i-r40-crypto`, `allwinner,sun20i-d1-crypto`, `allwinner,sun50i-a64-crypto`, `allwinner,sun50i-h5-crypto`, `allwinner,sun50i-h6-crypto`, `allwinner,sun50i-h616-crypto`); `reg` (max 1 items); `interrupts` (max 1 items); `clocks` (min 2 items); `clock-names` (min 2 items); `resets` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 2 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/sun50i-a64-ccu.h`, `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/reset/sun50i-a64-ccu.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `clock-names`, `resets` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ce.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ce.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/clock/sun50i-a64-ccu.h>; #include <dt-bindings/reset/sun50i-a64-ccu.h>; crypto: crypto@1c15000 {; compatible = "allwinner,sun8i-h3-crypto";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ce.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ss.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Allwinner
Security System v2 driver. It lives under `crypto` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/allwinner,sun8i-ss.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `allwinner,sun8i-a83t-crypto`, `allwinner,sun9i-a80-crypto`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `allwinner,sun8i-a83t-crypto`, `allwinner,sun9i-a80-crypto`); `reg` (max 1 items); `interrupts` (max 1 items); `resets` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/sun8i-a83t-ccu.h`, `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/reset/sun8i-a83t-ccu.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `clock-names`, `resets` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ss.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ss.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/clock/sun8i-a83t-ccu.h>; #include <dt-bindings/reset/sun8i-a83t-ccu.h>; crypto: crypto@1c15000 {; compatible = "allwinner,sun8i-a83t-crypto";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/allwinner,sun8i-ss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amd,ccp-seattle-v1a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amd,ccp-seattle-v1a.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: AMD
Cryptographic Coprocessor (ccp). It lives under `crypto` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/amd,ccp-seattle-v1a.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `amd,ccp-seattle-v1a`.
- Required properties: `compatible`, `reg`, `interrupts`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `iommus`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `dma-coherent`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `amd,ccp-seattle-v1a`); `reg` (max 1 items); `interrupts` (max 1 items); `iommus` (max 4 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/amd,ccp-seattle-v1a.yaml`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts` should
be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amd,ccp-seattle-v1a.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amd,ccp-seattle-v1a.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: crypto@e0100000 {; compatible = "amd,ccp-seattle-v1a";; reg = <0xe0100000 0x10000>;; interrupts = <0 3 4>;; dma-coherent;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amd,ccp-seattle-v1a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amlogic,gxl-crypto.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amlogic,gxl-crypto.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Amlogic
GXL Cryptographic Offloader. It lives under `crypto` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/amlogic,gxl-crypto.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `amlogic,gxl-crypto`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `clocks` (max 1 items); `clock-names` (const `blkmv`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/gxbb-clkc.h`, `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/interrupt-controller/irq.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `clock-names` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amlogic,gxl-crypto.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amlogic,gxl-crypto.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/clock/gxbb-clkc.h>; crypto: crypto-engine@c883e000 {; compatible = "amlogic,gxl-crypto";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/amlogic,gxl-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/arm,cryptocell.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/arm,cryptocell.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Arm
TrustZone CryptoCell cryptographic engine. It lives under `crypto` bindings and gives dt-schema
a machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The file does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/arm,cryptocell.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `arm,cryptocell-713-ree`, `arm,cryptocell-703-ree`, `arm,cryptocell-712-ree`, `arm,cryptocell-710-ree`, `arm,cryptocell-630p-ree`.
- Required properties: `compatible`, `reg`, `interrupts`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `power-domains`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `dma-coherent`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `arm,cryptocell-713-ree`, `arm,cryptocell-703-ree`, `arm,cryptocell-712-ree`, `arm,cryptocell-710-ree`, `arm,cryptocell-630p-ree`); `reg` (max 1 items); `interrupts` (max 1 items); `clocks` (max 1 items); `resets` (max 1 items); `power-domains` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts` should
be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/arm,cryptocell.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/arm,cryptocell.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; arm_cc712: crypto@80000000 {; compatible = "arm,cryptocell-712-ree";; reg = <0x80000000 0x10000>;; interrupts = <GIC_SPI 30 IRQ_TYPE_LEVEL_HIGH>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/arm,cryptocell.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2500-hace.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2500-hace.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: ASPEED
HACE hash and crypto Hardware Accelerator Engines. It lives under `crypto` bindings and gives
dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: The Hash and Crypto Engine (HACE) is designed to
accelerate the throughput of hash data digest, encryption, and decryption. Basically, HACE can
be divided into two independently engines - Hash Engine and Crypto Engine.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/aspeed,ast2500-hace.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `aspeed,ast2500-hace`, `aspeed,ast2600-hace`.
- Required properties: `compatible`, `reg`, `clocks`, `interrupts`, `resets`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `aspeed,ast2500-hace`, `aspeed,ast2600-hace`); `reg` (max 1 items); `interrupts` (max 1 items); `clocks` (max 1 items); `resets` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/ast2600-clock.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`,
`interrupts`, `resets` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2500-hace.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2500-hace.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/ast2600-clock.h>; hace: crypto@1e6d0000 {; compatible = "aspeed,ast2600-hace";; reg = <0x1e6d0000 0x200>;; interrupts = <4>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2500-hace.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2600-acry.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2600-acry.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: ASPEED
ACRY ECDSA/RSA Hardware Accelerator Engines. It lives under `crypto` bindings and gives dt-
schema a machine-readable contract for matching hardware nodes before those nodes reach kernel
drivers. The description says: The ACRY ECDSA/RSA engines is designed to accelerate the
throughput of ECDSA/RSA signature and verification. Basically, ACRY can be divided into two
independent engines - ECC Engine and RSA Engine.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/aspeed,ast2600-acry.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `aspeed,ast2600-acry`.
- Required properties: `compatible`, `reg`, `clocks`, `interrupts`, `aspeed,ahbc`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`.
- Vendor or device-specific extensions: `aspeed,ahbc`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `aspeed,ast2600-acry`); `interrupts` (max 1 items); `clocks` (max 1 items); `aspeed,ahbc` (ref `/schemas/types.yaml#/definitions/phandle`; A phandle to the AHB controller node, which must be a syscon).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/phandle`.
- Example/header integration: `dt-bindings/clock/ast2600-clock.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`,
`interrupts`, `aspeed,ahbc` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2600-acry.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2600-acry.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/ast2600-clock.h>; acry: crypto@1e6fa000 {; compatible = "aspeed,ast2600-acry";; reg = <0x1e6fa000 0x400>, <0x1e710000 0x1800>;; interrupts = <160>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/aspeed,ast2600-acry.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-aes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-aes.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Atmel
Advanced Encryption Standard (AES) HW cryptographic accelerator. It lives under `crypto`
bindings and gives dt-schema a machine-readable contract for matching hardware nodes before
those nodes reach kernel drivers. The file does not carry a long description, so its role is
inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/atmel,at91sam9g46-aes.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `atmel,at91sam9g46-aes`, `microchip,lan9691-aes`, `microchip,sam9x7-aes`, `microchip,sama7d65-aes`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `interrupts` (max 1 items); `clocks` (max 1 items); `clock-names` (const `aes_clk`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/at91.h`, `dt-bindings/dma/at91.h`, `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/interrupt-controller/irq.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `clock-names`, `dmas`, `dma-names` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-aes.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-aes.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/clock/at91.h>; #include <dt-bindings/dma/at91.h>; aes: crypto@e1810000 {

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-aes.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-sha.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-sha.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Atmel
Secure Hash Algorithm (SHA) HW cryptographic accelerator. It lives under `crypto` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The file does not carry a long description, so its role is inferred from title,
path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/atmel,at91sam9g46-sha.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `atmel,at91sam9g46-sha`, `microchip,lan9691-sha`, `microchip,sam9x7-sha`, `microchip,sama7d65-sha`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `interrupts` (max 1 items); `clocks` (max 1 items); `clock-names` (const `sha_clk`); `dmas` (max 1 items; TX DMA Channel); `dma-names` (const `tx`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/at91.h`, `dt-bindings/dma/at91.h`, `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/interrupt-controller/irq.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `clock-names` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-sha.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-sha.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/clock/at91.h>; #include <dt-bindings/dma/at91.h>; sha: crypto@e1814000 {

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-sha.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-tdes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-tdes.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Atmel
Triple Data Encryption Standard (TDES) HW cryptographic accelerator. It lives under `crypto`
bindings and gives dt-schema a machine-readable contract for matching hardware nodes before
those nodes reach kernel drivers. The file does not carry a long description, so its role is
inferred from title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/atmel,at91sam9g46-tdes.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `atmel,at91sam9g46-tdes`, `microchip,sam9x7-tdes`, `microchip,sama7d65-tdes`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `interrupts` (max 1 items); `clocks` (max 1 items); `clock-names` (const `tdes_clk`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/at91.h`, `dt-bindings/dma/at91.h`, `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/interrupt-controller/irq.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `clock-names` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-tdes.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-tdes.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/clock/at91.h>; #include <dt-bindings/dma/at91.h>; tdes: crypto@e2014000 {

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/atmel,at91sam9g46-tdes.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/axis,artpec6-crypto.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/axis,artpec6-crypto.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Axis
ARTPEC6 crypto engine with PDMA interface. It lives under `crypto` bindings and gives dt-schema
a machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The file does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/axis,artpec6-crypto.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `axis,artpec6-crypto`, `axis,artpec7-crypto`.
- Required properties: `compatible`, `reg`, `interrupts`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `axis,artpec6-crypto`, `axis,artpec7-crypto`); `reg` (max 1 items); `interrupts` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts` should
be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/axis,artpec6-crypto.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/axis,artpec6-crypto.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; crypto@f4264000 {; compatible = "axis,artpec6-crypto";; reg = <0xf4264000 0x1000>;; interrupts = <GIC_SPI 19 IRQ_TYPE_LEVEL_HIGH>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/axis,artpec6-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/brcm,spum-crypto.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/brcm,spum-crypto.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Broadcom
SPU Crypto Offload. It lives under `crypto` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The description
says: The Broadcom Secure Processing Unit (SPU) hardware supports symmetric cryptographic
offload for Broadcom SoCs. A SoC may have multiple SPU hardware blocks.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/brcm,spum-crypto.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,spum-crypto`, `brcm,spu2-crypto`, `brcm,spu2-v2-crypto`, `brcm,spum-nsp-crypto`.
- Required properties: `compatible`, `reg`, `mboxes`.
- Top-level framework properties: `compatible`, `reg`, `mboxes`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `brcm,spum-crypto`, `brcm,spu2-crypto`, `brcm,spu2-v2-crypto`, `brcm,spum-nsp-crypto`); `reg` (max 1 items); `mboxes` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/brcm,spum-crypto.yaml`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `mboxes` should be
caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/brcm,spum-crypto.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/brcm,spum-crypto.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: crypto@612d0000 {; compatible = "brcm,spum-crypto";; reg = <0x612d0000 0x900>;; mboxes = <&pdc0 0>;; };

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/brcm,spum-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/cortina,sl3516-crypto.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/cortina,sl3516-crypto.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: SL3516
cryptographic offloader driver. It lives under `crypto` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/cortina,sl3516-crypto.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `cortina,sl3516-crypto`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `cortina,sl3516-crypto`); `reg` (max 1 items); `interrupts` (max 1 items); `clocks` (max 1 items); `resets` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Example/header integration: `dt-bindings/clock/cortina,gemini-clock.h`, `dt-bindings/interrupt-controller/irq.h`, `dt-bindings/reset/cortina,gemini-reset.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks`, `resets` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/cortina,sl3516-crypto.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/cortina,sl3516-crypto.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/clock/cortina,gemini-clock.h>; #include <dt-bindings/reset/cortina,gemini-reset.h>; crypto@62000000 {; compatible = "cortina,sl3516-crypto";

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/cortina,sl3516-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec-v4.0-mon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec-v4.0-mon.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a crypto accelerator binding: Freescale
Secure Non-Volatile Storage (SNVS). It lives under `crypto` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: Node defines address range and the associated interrupt for the SNVS
function. This function monitors security state information & reports security violations. This
also included rtc, system power off and ON/OFF key.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/crypto/fsl,sec-v4.0-mon.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,sec-v4.0-mon`, `syscon`, `simple-mfd`, `fsl,sec-v5.0-mon`, `fsl,sec-v5.3-mon`, `fsl,sec-v5.4-mon`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `snvs-rtc-lp`, `snvs-powerkey`, `snvs-lpgpr`, `snvs-poweroff`.
- Child-node or pattern API: `snvs-rtc-lp` object requiring `compatible`, `interrupts`, `regmap`; `snvs-powerkey` object requiring `compatible`, `interrupts`, `regmap`.
- Property detail signals: `reg` (max 1 items); `interrupts` (max 2 items); `snvs-rtc-lp` (type `object`; Secure Non-Volatile Storage (SNVS) Low Power (LP) RTC Node); `snvs-powerkey` (ref `/schemas/input/input.yaml`; type `object`; The snvs-pwrkey is designed to enable POWER key function which controlled by SNVS ONOFF, the driver can report the st...); `snvs-lpgpr` (ref `/schemas/nvmem/snvs-lpgpr.yaml#`); `snvs-poweroff` (ref `/schemas/power/reset/syscon-poweroff.yaml#`; The SNVS could drive signal to PMIC to turn off system power by setting SNVS_LP LPCR register.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/input/input.yaml`, `/schemas/nvmem/snvs-lpgpr.yaml#`, `/schemas/power/reset/syscon-poweroff.yaml#`.
- Example/header integration: `dt-bindings/clock/imx7d-clock.h`, `dt-bindings/interrupt-controller/arm-gic.h`.
Runtime integration is with Linux crypto drivers, DMA/interrupt/clock/reset providers, and
hardware random/hash/cipher engines. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg` should be caught by
dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec-v4.0-mon.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec-v4.0-mon.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/clock/imx7d-clock.h>; sec_mon: sec-mon@314000 {; compatible = "fsl,sec-v4.0-mon", "syscon", "simple-mfd";; reg = <0x314000 0x1000>;

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec-v4.0-mon.yaml -->
