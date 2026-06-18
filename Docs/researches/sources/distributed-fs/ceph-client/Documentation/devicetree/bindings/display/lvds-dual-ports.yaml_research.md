<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds-dual-ports.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds-dual-ports.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds-dual-ports.yaml` is a Linux devicetree YAML schema for the `Dual-link LVDS Display Common Properties` LVDS display binding. Common properties for LVDS displays with dual LVDS links. Extend LVDS display common properties defined in lvds.yaml. Dual-link LVDS displays receive odd pixels and even pixels separately from the dual LVDS links. One link receives odd pixels and the other receives even pixels. Some of those displays may also use only one LVDS link to receive all pixels, being odd and even agnostic. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses no explicit compatible schema and covers 0 compatible tokens: no explicit compatible values. Top-level properties are `ports`. Top-level required properties are `ports`; nested required properties found across the schema include `dual-lvds-even-pixels`, `dual-lvds-odd-pixels`, `port@0`, `port@1`, `ports`. Graph integration is expressed through `ports`; endpoint-specific constraints include `dual-lvds-even-pixels`, `dual-lvds-odd-pixels`. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/ports`, `lvds.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 0 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 1 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level extra properties are intentionally allowed. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/lvds-dual-ports.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds-dual-ports.yaml -->
