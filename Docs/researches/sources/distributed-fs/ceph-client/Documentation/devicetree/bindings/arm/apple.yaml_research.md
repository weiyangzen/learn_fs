<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple.yaml` defines the root platform compatible binding titled `Apple ARM Machine`. ARM platforms using SoCs designed by Apple Inc., branded "Apple Silicon". This currently includes devices based on the "A7" SoC: - iPhone 5s - iPad Air (1) - iPad mini 2 - iPad mini 3 Devices based on the "A8" SoC: - iPhone 6 - iPhone 6 Plus - iPad mini 4 - iPod touch 6 - Apple TV HD Device based on the "A8X" SoC: - iPad Air 2 Devices based on the "A9" SoC: - iPhone 6s - iPhone 6s Plus - iPhone SE (2016) - iPad 5 Devices based on the "A9X" SoC: - iPad Pro (9.7-inch) - iPad Pro (12.9-inch) Devices based on the "A10" SoC: - iPhone 7 - iPhone 7 Plus - iPod touch 7 - iPad 6 - iPad 7 Devices based on the "A10X" SoC: - Apple TV 4K (1st generation) - iPad Pro (2nd Generation) (10.5 Inch) - iPad... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 18 accepted compatible sequences and lists 111 compatible tokens including `apple,j71`, `apple,j72`, `apple,j73`, `apple,j85`, `apple,j85m`, `apple,j86`, `apple,j86m`, `apple,j87`, `apple,j87m`, `apple,n51` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Hector Martin <marcan@marcan.st>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/apple.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple.yaml -->
