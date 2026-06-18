<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile.yaml` defines the root platform compatible binding titled `ARM Versatile Boards`. The ARM Versatile boards are two variants of ARM926EJ-S evaluation boards with various pluggable interface boards, in essence the Versatile PB version is a superset of the Versatile AB version. The root node in the Versatile platforms must contain a core module child node. They are always at physical address 0x10000000 in all the Versatile variants. When fitted with the IB2 Interface Board, the Versatile AB will present an optional system controller node which controls the extra peripherals on the interface board. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 2 accepted compatible sequences and lists 2 compatible tokens including `arm,versatile-ab`, `arm,versatile-pb`. Top-level schema properties are `$nodename`, `compatible`; required properties are `compatible`, `core-module@10000000`.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,versatile.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile.yaml -->
