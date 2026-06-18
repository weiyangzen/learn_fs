<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel-at91.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel-at91.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel-at91.yaml` defines the root platform compatible binding titled `Atmel AT91.`. Boards with a SoC of the Atmel AT91 or SMART family shall have the following The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 36 accepted compatible sequences and lists 108 compatible tokens including `atmel,at91rm9200`, `atmel,at91sam9260`, `atmel,at91sam9261`, `atmel,at91sam9263`, `atmel,at91sam9g20`, `atmel,at91sam9g45`, `atmel,at91sam9n12`, `atmel,at91sam9rl`, `atmel,at91sam9xe`, `atmel,at91sam9x60` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>, Claudiu Beznea <claudiu.beznea@microchip.com>, Nicolas Ferre <nicolas.ferre@microchip.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/atmel-at91.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel-at91.yaml -->
