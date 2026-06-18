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
