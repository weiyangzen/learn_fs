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
