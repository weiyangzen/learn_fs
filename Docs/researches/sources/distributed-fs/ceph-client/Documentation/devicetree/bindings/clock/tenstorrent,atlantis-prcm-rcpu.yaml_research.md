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
