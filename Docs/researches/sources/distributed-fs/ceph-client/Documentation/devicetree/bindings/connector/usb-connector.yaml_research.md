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
