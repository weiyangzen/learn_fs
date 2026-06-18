# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,madera.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Cirrus Logic
Madera class audio CODECs pinctrl driver. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The Cirrus Logic Madera codecs provide a number of GPIO functions for interfacing to external
hardware and to provide logic outputs to other devices. Certain groups of GPIO pins also have an
alternate function, normally as an audio interface. The set of available GPIOs, functions and
alternate function groups differs between CODECs so refer to the datasheet for the CODEC for further
information on what is supported on that device. The properties for this driver exist within the
parent MFD driver node. See also the core bindings for the parent MFD driver:
Documentation/devicetree/bindings/mfd/cirrus,madera.yaml And the generic pinmix bindings:
Documentation/devicetree/bindings/pinctrl/pinctrl-bindings.txt

The binding is maintained in-source by patches@opensource.cirrus.com.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/cirrus,madera.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: none declared.
- Required properties: `pinctrl-0`, `pinctrl-names`.
- Top-level framework properties: none declared.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `pin-settings`.
- Child-node or reusable schema API: object-valued child/property schemas `pin-settings`.
- Property detail signals: pin-settings (One subnode is required to contain the default settings. It contains an arbitrary number of confi...).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: true` allows extensions beyond declared keys.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/cirrus,madera.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `pinctrl-0`, `pinctrl-names` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,madera.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,madera.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, add a bogus pin group/function, and add an undeclared property where closure is enabled.
