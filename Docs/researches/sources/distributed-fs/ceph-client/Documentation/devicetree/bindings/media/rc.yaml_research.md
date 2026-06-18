# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rc.yaml`, a media ancillary controller devicetree binding. The schema title is `Generic Infrared Remote Controller`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Generic Infrared Remote Controller`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- property surface: `$nodename`, `linux,rc-map-name` (ref /schemas/types.yaml#/definitions/string; enum rc-adstech-dvb-t-pci, rc-alink-dtu-m, rc-anysee, rc-apac-viewcomp, rc-astrometa-t2hybrid, rc-asus-pc39, rc-asus-ps3-100, rc-ati-tv-wonder-hd-600, and 132 more).
- referenced schemas: /schemas/types.yaml#/definitions/string.
- Structural features: no graph child-node or composition machinery beyond top-level property validation.
- Schema closure: inherits openness from composed references or leaves additional properties unconstrained where allowed.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file has no inline example block, so coverage depends on external DTS users and schemas that reference it.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Mauro Carvalho Chehab <mchehab@kernel.org>, Sean Young <sean@mess.org>.
- schema id: http://devicetree.org/schemas/media/rc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/string.

## Risks And Edge Cases
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `none declared`, optional top-level properties include `$nodename, linux,rc-map-name`, and compatible coverage is `none declared`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/string.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.
