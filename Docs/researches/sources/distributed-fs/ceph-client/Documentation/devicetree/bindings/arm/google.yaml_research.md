<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/google.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/google.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/google.yaml` defines the root platform compatible binding titled `Google Tensor platforms`. ARM platforms using SoCs designed by Google branded "Tensor" used in Pixel devices. Currently upstream this is devices using "gs101" SoC which is found in Pixel 6, Pixel 6 Pro and Pixel 6a. Google have a few different names for the SoC: - Marketing name ("Tensor") - Codename ("Whitechapel") - SoC ID ("gs101") - Die ID ("S5P9845") Likewise there are a couple of names for the actual device - Marketing name ("Pixel 6") - Codename ("Oriole") Devicetrees should use the lowercased SoC ID and lowercased board codename, e.g. gs101 and gs101-oriole. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 1 accepted compatible sequence and lists 3 compatible tokens including `google,gs101-oriole`, `google,gs101-raven`, `google,gs101`. Top-level schema properties are `$nodename`, `compatible`, `ect`; required properties are `ect`.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Peter Griffin <peter.griffin@linaro.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/google.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/google.yaml -->
