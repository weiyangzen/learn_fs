<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml` defines the root platform compatible binding titled `Broadcom Broadband SoC`. Broadcom Broadband SoCs include family of high performance DSL/PON/Wireless chips that can be used as home gateway, router and WLAN AP for residential, enterprise and carrier applications. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 17 accepted compatible sequences and lists 41 compatible tokens including `brcm,bcm947622`, `brcm,bcm47622`, `brcm,bcmbca`, `netgear,r8000p`, `tplink,archer-c2300-v1`, `zyxel,ex3510b`, `brcm,bcm4906`, `brcm,bcm4908`, `asus,gt-ac5300`, `brcm,bcm94908` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: William Zhang <william.zhang@broadcom.com>, Anand Gore <anand.gore@broadcom.com>, Kursad Oney <kursad.oney@broadcom.com>, Rafał Miłecki <rafal@milecki.pl>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml -->
