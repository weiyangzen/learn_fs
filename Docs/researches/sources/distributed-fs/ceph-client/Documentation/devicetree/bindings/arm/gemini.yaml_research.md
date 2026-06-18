<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/gemini.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/gemini.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/gemini.yaml` defines the root platform compatible binding titled `Cortina systems Gemini platforms`. The Gemini SoC is the project name for an ARMv4 FA525-based SoC originally produced by Storlink Semiconductor around 2005. The company was renamed later renamed Storm Semiconductor. The chip product name is Storlink SL3516. It was derived from earlier products from Storm named SL3316 (Centroid) and SL3512 (Bulverde). Storm Semiconductor was acquired by Cortina Systems in 2008 and the SoC was produced and used for NAS and similar usecases. In 2014 Cortina Systems was in turn acquired by Inphi, who seem to have discontinued this product family. Many of the IP blocks used in the SoC comes from Faraday Technology. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 12 accepted compatible sequences and lists 14 compatible tokens including `storlink,gemini324`, `storm,sl93512r`, `cortina,gemini`, `dlink,dir-685`, `dlink,dns-313`, `edimax,ns-2502`, `itian,sq201`, `raidsonic,ib-4220-b`, `ssi,1328`, `teltonika,rut1xx` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/gemini.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/gemini.yaml -->
