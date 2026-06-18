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
