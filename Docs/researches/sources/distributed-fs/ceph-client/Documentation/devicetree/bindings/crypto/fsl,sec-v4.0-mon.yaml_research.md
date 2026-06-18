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
