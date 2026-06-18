## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinmux-node.yaml

### Purpose
`pinmux-node.yaml` is the generic pin multiplexing state-node helper. It standardizes the reusable vocabulary for selecting mux functions on named pins, named groups, packed numeric `pinmux` values, or hardware-indexed `pinctrl-pin-array` entries.

### Important Schema APIs
The schema defines `function` as a string, `pins` as either a string-array or uint32-array, `groups` as a string-array, `pinmux` as a uint32-array, and `pinctrl-pin-array` as a uint32-array. Hardware-specific schemas decide the legal pin IDs, group names, packed bit layout, and function enum.

### Validation Flow
The validation path is intentionally shallow: core dt-schema checks this helper, then concrete bindings add enum and pattern restrictions through `allOf` or `$defs`. The descriptive text explains three accepted mux forms and why `pinctrl-pin-array` uses hardware register indexes instead of virtual pin indexes. `additionalProperties: true` leaves pin configuration properties and vendor extensions available to companion schemas.

### State And Persistence
This file stores no runtime state. It persists a schema vocabulary used by DTS files and by drivers that parse state nodes into Linux pinctrl maps. Numeric `pinmux` and `pinctrl-pin-array` values persist hardware-specific encodings that drivers must decode consistently.

### Dependencies And Integration Points
It depends on `/schemas/types.yaml` for string and integer array typing. The Qualcomm TLMM, Qualcomm PMIC, LPASS LPI, NXP SIUL2, and generic `pinctrl-single` bindings in this batch all compose with this helper for their state nodes.

### Risks
The helper cannot enforce that one of `pins`, `groups`, or `pinmux` is present; concrete bindings must add required clauses where their drivers need them. Packed integer mux formats are opaque to dt-schema, so mistakes in macro definitions or bit assignments require binding examples and driver tests to catch.

### Test Signals
Run dt-schema checks against this helper and at least one concrete binding for each mux form: string pins with function, group-based functions, packed `pinmux`, and `pinctrl-pin-array`. DTS examples should include invalid types to prove the string-array and uint32-array constraints fire.
