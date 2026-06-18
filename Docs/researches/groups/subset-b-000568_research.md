# Research: subset-b-000568

Grouped research for display-related devicetree binding schemas. Each section preserves the source path and marker pair required for deterministic reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it6505.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it6505.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it6505.yaml` is a Linux devicetree YAML schema for the `ITE it6505` display bridge binding. The IT6505 is a high-performance DisplayPort 1.1a transmitter, fully compliant with DisplayPort 1.1a, HDCP 1.3 specifications. The IT6505 supports color depth of up to 36 bits (12 bits/color) and ensures robust transmission of high-quality uncompressed video content, along with uncompressed and compressed digital audio content. Aside from the various video output formats supported, the IT6505 also encodes and transmits up to 8 channels of I2S digital audio, with sampling rate up to 192kHz and sample size up to 24 bits. In addition, an S/PDIF input port takes in compressed audio of up to 192kHz frame rate. Each IT6505 chip comes preprogrammed with an unique HDCP key, in compliance with the HDCP 1.3 standard so as to provide secure transmission of h... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `ite,it6505`. Top-level properties are `compatible`, `reg`, `ovdd-supply`, `pwr18-supply`, `interrupts`, `reset-gpios`, `extcon`, `#sound-dai-cells`, `ports`. Top-level required properties are `compatible`, `ovdd-supply`, `pwr18-supply`, `interrupts`, `reset-gpios`, `extcon`, `ports`; nested required properties found across the schema include `compatible`, `extcon`, `interrupts`, `ovdd-supply`, `port@0`, `port@1`, `ports`, `pwr18-supply`, `reset-gpios`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-lanes`, `link-frequencies`. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `ovdd-supply`, `pwr18-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Allen Chen <allen.chen@ite.com.tw>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/ports`, `/schemas/sound/dai-common.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 9 top-level properties and 14 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ite,it6505.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it6505.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it66121.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it66121.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it66121.yaml` is a Linux devicetree YAML schema for the `ITE it66121 HDMI bridge` HDMI/display bridge binding. The IT66121 is a high-performance and low-power single channel HDMI transmitter, fully compliant with HDMI 1.3a, HDCP 1.2 and backward compatible to DVI 1.0 specifications. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 3 compatible tokens: `ite,it66121`, `ite,it66122`, `ite,it6610`. Top-level properties are `compatible`, `reg`, `reset-gpios`, `vrf12-supply`, `vcn33-supply`, `vcn18-supply`, `interrupts`, `#sound-dai-cells`, `ports`. Top-level required properties are `compatible`, `reg`, `reset-gpios`, `vrf12-supply`, `vcn33-supply`, `vcn18-supply`, `interrupts`, `ports`; nested required properties found across the schema include `compatible`, `interrupts`, `port@0`, `port@1`, `ports`, `reg`, `reset-gpios`, `vcn18-supply`, `vcn33-supply`, `vrf12-supply`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `bus-width`. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vrf12-supply`, `vcn33-supply`, `vcn18-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Phong LE <ple@baylibre.com>, Neil Armstrong <neil.armstrong@linaro.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/sound/dai-common.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 9 top-level properties and 13 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ite,it66121.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it66121.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt8713sx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt8713sx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt8713sx.yaml` is a Linux devicetree YAML schema for the `Lontium LT8713SX Type-C/DP1.4 to Type-C/DP1.4/HDMI2.0/DP++ bridge-hub` HDMI/display bridge binding. The Lontium LT8713SX is a Type-C/DP1.4 to Type-C/DP1.4/HDMI2.0 converter that integrates one DP input and up to three configurable output interfaces (DP1.4 / HDMI2.0 / DP++), with SST/MST functionality and audio support. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 1 compatible token: `lontium,lt8713sx`. Top-level properties are `compatible`, `reg`, `vcc-supply`, `vdd-supply`, `reset-gpios`, `ports`. Top-level required properties are `compatible`, `reg`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `ports`, `reg`. Graph integration is expressed through `port@0`, `port@1`, `port@2`, `port@3`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vcc-supply`, `vdd-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Vishnu Saini <vishnu.saini@oss.qualcomm.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/lontium,lt8713sx.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt8713sx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt8912b.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt8912b.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt8912b.yaml` is a Linux devicetree YAML schema for the `Lontium LT8912B MIPI to HDMI Bridge` MIPI DSI/display bridge binding. The LT8912B is a bridge device which convert DSI to HDMI It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 1 compatible token: `lontium,lt8912b`. Top-level properties are `compatible`, `reg`, `reset-gpios`, `ports`, `vcchdmipll-supply`, `vcchdmitx-supply`, `vcclvdspll-supply`, `vcclvdstx-supply`, `vccmipirx-supply`, `vccsysclk-supply`, `vdd-supply`. Top-level required properties are `compatible`, `reg`, `ports`; nested required properties found across the schema include `compatible`, `data-lanes`, `port@0`, `port@1`, `ports`, `reg`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vcchdmipll-supply`, `vcchdmitx-supply`, `vcclvdspll-supply`, `vcclvdstx-supply`, `vccmipirx-supply`, `vccsysclk-supply`, `vdd-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Adrien Grassein <adrien.grassein@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 11 top-level properties and 14 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/lontium,lt8912b.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt8912b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt9211.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt9211.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt9211.yaml` is a Linux devicetree YAML schema for the `Lontium LT9211 DSI/LVDS/DPI to DSI/LVDS/DPI bridge.` MIPI DSI/display bridge binding. The LT9211 are bridge devices which convert Single/Dual-Link DSI/LVDS or Single DPI to Single/Dual-Link DSI/LVDS or Single DPI. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 1 compatible token: `lontium,lt9211`. Top-level properties are `compatible`, `reg`, `interrupts`, `reset-gpios`, `vccio-supply`, `ports`. Top-level required properties are `compatible`, `reg`, `vccio-supply`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@2`, `ports`, `reg`, `vccio-supply`. Graph integration is expressed through `port@0`, `port@1`, `port@2`, `port@3`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vccio-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Marek Vasut <marex@denx.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/lontium,lt9211.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt9211.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt9611.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt9611.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt9611.yaml` is a Linux devicetree YAML schema for the `Lontium LT9611(UXC) 2 Port MIPI to HDMI Bridge` MIPI DSI/display bridge binding. The LT9611 and LT9611UXC are bridge devices which convert DSI to HDMI It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `lontium,lt9611`, `lontium,lt9611uxc`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `interrupts`, `reset-gpios`, `vdd-supply`, `vcc-supply`, `ports`. Top-level required properties are `compatible`, `reg`, `interrupts`, `vdd-supply`, `vcc-supply`, `ports`; nested required properties found across the schema include `compatible`, `interrupts`, `port@0`, `port@1`, `port@2`, `ports`, `reg`, `vcc-supply`, `vdd-supply`. Graph integration is expressed through `port@0`, `port@1`, `port@2`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vdd-supply`, `vcc-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Vinod Koul <vkoul@kernel.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/sound/dai-common.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 11 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/lontium,lt9611.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lontium,lt9611.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lvds-codec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lvds-codec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lvds-codec.yaml` is a Linux devicetree YAML schema for the `Transparent LVDS encoders and decoders` LVDS/display bridge binding. This binding supports transparent LVDS encoders and decoders that don't require any configuration. LVDS is a physical layer specification defined in ANSI/TIA/EIA-644-A. Multiple incompatible data link layers have been used over time to transmit image data to LVDS panels. This binding targets devices compatible with the following specifications only. [JEIDA] "Digital Interface Standards for Monitor", JEIDA-59-1999, February 1999 (Version 1.0), Japan Electronic Industry Development Association (JEIDA) [LDI] "Open LVDS Display Interface", May 1999 (Version 0.95), National Semiconductor [VESA] "VESA Notebook Panel Standard", October 2007 (Version 1.0), Video Electronics Standards Association (VESA) Those devices have been marketed under the FPD-Link a... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 3 accepted compatible forms and covers 12 compatible tokens: `doestek,dtc34lm85am`, `onnn,fin3385`, `ti,ds90c185`, `ti,ds90c187`, `ti,sn75lvds83`, `lvds-encoder`, `ti,ds90cf364a`, `ti,ds90cf384a`, `ti,sn65lvds822`, `ti,sn65lvds94`, `lvds-decoder`, `thine,thc63lvdm83d`. Top-level properties are `compatible`, `ports`, `pclk-sample`, `powerdown-gpios`, `power-supply`. Top-level required properties are `compatible`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-mapping`. Resource hooks include clocks: none; resets: none; regulators/power: `power-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/lvds-codec.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/lvds-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/megachips,stdp2690-ge-b850v3-fw.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/megachips,stdp2690-ge-b850v3-fw.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/megachips,stdp2690-ge-b850v3-fw.yaml` is a Linux devicetree YAML schema for the `GE B850v3 video bridge` display bridge binding. STDP4028-ge-b850v3-fw bridges (LVDS-DP) STDP2690-ge-b850v3-fw bridges (DP-DP++) The video processing pipeline on the second output on the GE B850v3: Host -> LVDS|--(STDP4028)--|DP -> DP|--(STDP2690)--|DP++ -> Video output Each bridge has a dedicated flash containing firmware for supporting the custom design. The result is that, in this design, neither the STDP4028 nor the STDP2690 behave as the stock bridges would. The compatible strings include the suffix "-ge-b850v3-fw" to make it clear that the driver is for the bridges with the firmware specific for the GE B850v3. The hardware do not provide control over the video processing pipeline, as the two bridges behaves as a single one. The only interfaces exposed by the hardware are EDID, HPD, and int... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `megachips,stdp4028-ge-b850v3-fw`, `megachips,stdp2690-ge-b850v3-fw`. Top-level properties are `compatible`, `reg`, `interrupts`, `ports`. Top-level required properties are `compatible`, `reg`, `ports`; nested required properties found across the schema include `compatible`, `interrupts`, `port@0`, `port@1`, `ports`, `reg`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/megachips,stdp2690-ge-b850v3-fw.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/megachips,stdp2690-ge-b850v3-fw.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/microchip,sam9x75-lvds.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/microchip,sam9x75-lvds.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/microchip,sam9x75-lvds.yaml` is a Linux devicetree YAML schema for the `Microchip SAM9X75 LVDS Controller` LVDS/display bridge binding. The Low Voltage Differential Signaling Controller (LVDSC) manages data format conversion from the LCD Controller internal DPI bus to OpenLDI LVDS output signals. LVDSC functions include bit mapping, balanced mode management, and serializer. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `microchip,sam9x75-lvds`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Top-level required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Dharma Balasubiramani <dharma.b@microchip.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 5 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/microchip,sam9x75-lvds.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/microchip,sam9x75-lvds.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nwl-dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nwl-dsi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nwl-dsi.yaml` is a Linux devicetree YAML schema for the `Northwest Logic MIPI-DSI controller on i.MX SoCs` MIPI DSI/display bridge binding. NWL MIPI-DSI host controller found on i.MX8 platforms. This is a dsi bridge for the SOCs NWL MIPI-DSI host controller. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8mq-nwl-dsi`. Top-level properties are `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`, `assigned-clock-parents`, `assigned-clock-rates`, `assigned-clocks`, `clocks`, `clock-names`, `mux-controls`, `phys`, `phy-names`, `power-domains`, `resets`, `reset-names`, `ports`. Top-level required properties are `#address-cells`, `#size-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `mux-controls`, `phy-names`, `phys`, `ports`, `reg`, `reset-names`, `resets`; nested required properties found across the schema include `#address-cells`, `#size-cells`, `clock-names`, `clocks`, `compatible`, `endpoint@0`, `endpoint@1`, `interrupts`, `mux-controls`, `phy-names`, `phys`, `port@0`, `port@1`, `ports`, `reg`, `reset-names`, `resets`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: `assigned-clock-parents`, `assigned-clock-rates`, `assigned-clocks`, `clocks`, `clock-names`; resets: `resets`, `reset-names`; regulators/power: `power-domains`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Guido Gúnther <agx@sigxcpu.org>, Robert Chiras <robert.chiras@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `../dsi-controller.yaml#`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/endpoint`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 17 top-level properties and 23 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/nwl-dsi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nwl-dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nxp,ptn3460.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nxp,ptn3460.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nxp,ptn3460.yaml` is a Linux devicetree YAML schema for the `NXP PTN3460 eDP to LVDS bridge` LVDS/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `nxp,ptn3460`. Top-level properties are `compatible`, `reg`, `edid-emulation`, `powerdown-gpios`, `reset-gpios`, `ports`. Top-level required properties are `compatible`, `reg`, `edid-emulation`, `powerdown-gpios`, `reset-gpios`, `ports`; nested required properties found across the schema include `compatible`, `edid-emulation`, `port@0`, `port@1`, `ports`, `powerdown-gpios`, `reg`, `reset-gpios`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Sean Paul <seanpaul@chromium.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 8 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/nxp,ptn3460.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nxp,ptn3460.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nxp,tda998x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nxp,tda998x.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nxp,tda998x.yaml` is a Linux devicetree YAML schema for the `NXP TDA998x HDMI transmitter` HDMI/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `nxp,tda998x`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `video-ports`, `audio-ports`, `#sound-dai-cells`, `nxp,calib-gpios`, `port`, `ports`. Top-level required properties are `compatible`, `reg`; nested required properties found across the schema include `compatible`, `port`, `ports`, `reg`. Graph integration is expressed through `port`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Russell King <linux@armlinux.org.uk>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/sound/dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-matrix`. Pattern properties are none; top-level composition/conditional keys are `allOf`, `oneOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 10 top-level properties and 12 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/nxp,tda998x.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/nxp,tda998x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/parade,ps8622.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/parade,ps8622.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/parade,ps8622.yaml` is a Linux devicetree YAML schema for the `Parade PS8622/PS8625 DisplayPort to LVDS Converter` LVDS/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `parade,ps8622`, `parade,ps8625`. Top-level properties are `compatible`, `reg`, `lane-count`, `use-external-pwm`, `reset-gpios`, `sleep-gpios`, `vdd12-supply`, `ports`. Top-level required properties are `compatible`, `reg`, `reset-gpios`, `sleep-gpios`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`, `reg`, `reset-gpios`, `sleep-gpios`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vdd12-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Krzysztof Kozlowski <krzk@kernel.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/parade,ps8622.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/parade,ps8622.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ps8640.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ps8640.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ps8640.yaml` is a Linux devicetree YAML schema for the `MIPI DSI to eDP Video Format Converter` MIPI DSI/display bridge binding. The PS8640 is a low power MIPI-to-eDP video format converter supporting mobile devices with embedded panel resolutions up to 2048 x 1536. The device accepts a single channel of MIPI DSI v1.1, with up to four lanes plus clock, at a transmission rate up to 1.5Gbit/sec per lane. The device outputs eDP v1.4, one or two lanes, at a link rate of up to 3.24Gbit/sec per lane. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `parade,ps8640`. Top-level properties are `compatible`, `reg`, `powerdown-gpios`, `reset-gpios`, `vdd12-supply`, `vdd33-supply`, `aux-bus`, `ports`. Top-level required properties are `compatible`, `reg`, `powerdown-gpios`, `reset-gpios`, `vdd12-supply`, `vdd33-supply`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `ports`, `powerdown-gpios`, `reg`, `reset-gpios`, `vdd12-supply`, `vdd33-supply`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vdd12-supply`, `vdd33-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Nicolas Boichat <drinkcat@chromium.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/display/dp-aux-bus.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ps8640.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ps8640.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dsi-csi2-tx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dsi-csi2-tx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dsi-csi2-tx.yaml` is a Linux devicetree YAML schema for the `Renesas R-Car MIPI DSI/CSI-2 Encoder` MIPI DSI/display bridge binding. This binding describes the MIPI DSI/CSI-2 encoder embedded in the Renesas R-Car Gen4 SoCs. The encoder can operate in either DSI or CSI-2 mode, with up to four data lanes. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 3 compatible tokens: `renesas,r8a779a0-dsi-csi2-tx`, `renesas,r8a779g0-dsi-csi2-tx`, `renesas,r8a779h0-dsi-csi2-tx`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `resets`, `ports`. Top-level required properties are `compatible`, `reg`, `clocks`, `power-domains`, `resets`, `ports`; nested required properties found across the schema include `clocks`, `compatible`, `data-lanes`, `port@0`, `port@1`, `ports`, `power-domains`, `reg`, `resets`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: `clocks`, `clock-names`; resets: `resets`; regulators/power: `power-domains`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/display/dsi-controller.yaml#`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 11 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/renesas,dsi-csi2-tx.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dsi-csi2-tx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dsi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dsi.yaml` is a Linux devicetree YAML schema for the `Renesas RZ/G2L MIPI DSI Encoder` MIPI DSI/display bridge binding. This binding describes the MIPI DSI encoder embedded in the Renesas RZ/G2L alike family of SoC's. The encoder can operate in DSI mode, with up to four data lanes. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 3 accepted compatible forms and covers 5 compatible tokens: `renesas,r9a07g044-mipi-dsi`, `renesas,r9a07g054-mipi-dsi`, `renesas,rzg2l-mipi-dsi`, `renesas,r9a09g056-mipi-dsi`, `renesas,r9a09g057-mipi-dsi`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `ports`. Top-level required properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `ports`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `data-lanes`, `interrupt-names`, `interrupts`, `port@0`, `port@1`, `ports`, `power-domains`, `reg`, `reset-names`, `resets`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: `clocks`, `clock-names`; resets: `resets`, `reset-names`; regulators/power: `power-domains`; IRQ/DMA-related: `interrupts`, `interrupt-names`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Biju Das <biju.das.jz@bp.renesas.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `../dsi-controller.yaml#`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 10 top-level properties and 14 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/renesas,dsi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dw-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dw-hdmi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dw-hdmi.yaml` is a Linux devicetree YAML schema for the `Renesas R-Car DWC HDMI TX Encoder` HDMI/display bridge binding. The HDMI transmitter is a Synopsys DesignWare HDMI 1.4 TX controller IP with a companion PHY IP. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses ordered `items` sequence and covers 8 compatible tokens: `renesas,r8a774a1-hdmi`, `renesas,r8a774b1-hdmi`, `renesas,r8a774e1-hdmi`, `renesas,r8a7795-hdmi`, `renesas,r8a7796-hdmi`, `renesas,r8a77961-hdmi`, `renesas,r8a77965-hdmi`, `renesas,rcar-gen3-hdmi`. Top-level properties are `compatible`, `reg-io-width`, `clocks`, `clock-names`, `resets`, `ports`, `power-domains`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `interrupts`, `ports`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `port@0`, `port@1`, `port@2`, `ports`, `reg`, `resets`. Graph integration is expressed through `port@0`, `port@1`, `port@2`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: `resets`; regulators/power: `power-domains`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `synopsys,dw-hdmi.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/renesas,dw-hdmi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,dw-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,lvds.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,lvds.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,lvds.yaml` is a Linux devicetree YAML schema for the `Renesas R-Car LVDS Encoder` LVDS/display bridge binding. These DT bindings describe the LVDS encoder embedded in the Renesas R-Car Gen2, R-Car Gen3, RZ/G1 and RZ/G2 SoCs. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 18 compatible tokens: `renesas,r8a7742-lvds`, `renesas,r8a7743-lvds`, `renesas,r8a7744-lvds`, `renesas,r8a774a1-lvds`, `renesas,r8a774b1-lvds`, `renesas,r8a774c0-lvds`, `renesas,r8a774e1-lvds`, `renesas,r8a7790-lvds`, `renesas,r8a7791-lvds`, `renesas,r8a7793-lvds`, `renesas,r8a7795-lvds`, `renesas,r8a7796-lvds`, `renesas,r8a77961-lvds`, `renesas,r8a77965-lvds`, `renesas,r8a77970-lvds`, `renesas,r8a77980-lvds`, `renesas,r8a77990-lvds`, `renesas,r8a77995-lvds`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `ports`, `power-domains`, `renesas,companion`. Top-level required properties are `compatible`, `reg`, `clocks`, `power-domains`, `resets`, `ports`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `port@0`, `port@1`, `ports`, `power-domains`, `reg`, `resets`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: `resets`; regulators/power: `power-domains`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are `if`, `then`, `else`; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/renesas,lvds.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/renesas,lvds.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/samsung,mipi-dsim.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/samsung,mipi-dsim.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/samsung,mipi-dsim.yaml` is a Linux devicetree YAML schema for the `Samsung MIPI DSIM bridge controller` MIPI DSI/display bridge binding. Samsung MIPI DSIM bridge controller can be found it on Exynos and i.MX8M Mini/Nano/Plus SoC's. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 10 compatible tokens: `samsung,exynos3250-mipi-dsi`, `samsung,exynos4210-mipi-dsi`, `samsung,exynos5410-mipi-dsi`, `samsung,exynos5422-mipi-dsi`, `samsung,exynos5433-mipi-dsi`, `samsung,exynos7870-mipi-dsi`, `fsl,imx8mm-mipi-dsim`, `fsl,imx8mp-mipi-dsim`, `fsl,imx7d-mipi-dsim`, `fsl,imx8mn-mipi-dsim`. Top-level properties are `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`, `samsung,phy-type`, `power-domains`, `samsung,power-domain`, `vddcore-supply`, `vddio-supply`, `samsung,burst-clock-frequency`, `samsung,esc-clock-frequency`, `samsung,pll-clock-frequency`, `phys`, `phy-names`, `ports`. Top-level required properties are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `samsung,esc-clock-frequency`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `port@0`, `ports`, `reg`, `samsung,esc-clock-frequency`, `samsung,phy-type`, `vddcore-supply`, `vddio-supply`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: `clocks`, `clock-names`, `samsung,burst-clock-frequency`, `samsung,esc-clock-frequency`, `samsung,pll-clock-frequency`; resets: none; regulators/power: `power-domains`, `vddcore-supply`, `vddio-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Inki Dae <inki.dae@samsung.com>, Jagan Teki <jagan@amarulasolutions.com>, Marek Szyprowski <m.szyprowski@samsung.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `../dsi-controller.yaml#`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 18 top-level properties and 23 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: additional top-level entries are constrained by a nested schema. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/samsung,mipi-dsim.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/samsung,mipi-dsim.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii8620.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii8620.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii8620.yaml` is a Linux devicetree YAML schema for the `Silicon Image SiI8620 HDMI/MHL bridge` HDMI/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `sil,sii8620`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `cvcc10-supply`, `interrupts`, `iovcc18-supply`, `reset-gpios`, `ports`. Top-level required properties are `compatible`, `reg`, `clocks`, `cvcc10-supply`, `interrupts`, `iovcc18-supply`, `reset-gpios`, `ports`; nested required properties found across the schema include `clocks`, `compatible`, `cvcc10-supply`, `interrupts`, `iovcc18-supply`, `port@0`, `port@1`, `ports`, `reg`, `reset-gpios`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: `reset-gpios`; regulators/power: `cvcc10-supply`, `iovcc18-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Krzysztof Kozlowski <krzk@kernel.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 9 top-level properties and 11 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/sil,sii8620.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii8620.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii9022.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii9022.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii9022.yaml` is a Linux devicetree YAML schema for the `Silicon Image sii902x HDMI bridge` HDMI/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 3 compatible tokens: `sil,sii9022-cpi`, `sil,sii9022-tpi`, `sil,sii9022`. Top-level properties are `compatible`, `reg`, `interrupts`, `reset-gpios`, `iovcc-supply`, `cvcc12-supply`, `#sound-dai-cells`, `sil,i2s-data-lanes`, `clocks`, `clock-names`, `ports`. Top-level required properties are `compatible`, `reg`; nested required properties found across the schema include `compatible`, `reg`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `port@3`, `ports`; endpoint-specific constraints include `bus-width`. Resource hooks include clocks: `clocks`, `clock-names`; resets: `reset-gpios`; regulators/power: `iovcc-supply`, `cvcc12-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Boris Brezillon <bbrezillon@kernel.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/sound/dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 11 top-level properties and 16 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/sil,sii9022.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii9022.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii9234.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii9234.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii9234.yaml` is a Linux devicetree YAML schema for the `Silicon Image SiI9234 HDMI/MHL bridge` HDMI/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `sil,sii9234`. Top-level properties are `compatible`, `reg`, `avcc12-supply`, `avcc33-supply`, `cvcc12-supply`, `iovcc18-supply`, `interrupts`, `reset-gpios`, `ports`. Top-level required properties are `compatible`, `reg`, `avcc12-supply`, `avcc33-supply`, `cvcc12-supply`, `iovcc18-supply`, `interrupts`, `reset-gpios`, `ports`; nested required properties found across the schema include `avcc12-supply`, `avcc33-supply`, `compatible`, `cvcc12-supply`, `interrupts`, `iovcc18-supply`, `port@0`, `ports`, `reg`, `reset-gpios`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `avcc12-supply`, `avcc33-supply`, `cvcc12-supply`, `iovcc18-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Maciej Purski <m.purski@samsung.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 9 top-level properties and 11 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/sil,sii9234.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/sil,sii9234.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/simple-bridge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/simple-bridge.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/simple-bridge.yaml` is a Linux devicetree YAML schema for the `Transparent non-programmable DRM bridges` display bridge binding. This binding supports transparent non-programmable bridges that don't require any configuration, with a single input and a single output. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 3 accepted compatible forms and covers 13 compatible tokens: `ti,ths8134a`, `ti,ths8134b`, `ti,ths8134`, `corpro,gm7123`, `adi,adv7123`, `algoltek,ag6311`, `asl-tek,cs5263`, `dumb-vga-dac`, `parade,ps185hdm`, `radxa,ra620`, `realtek,rtd2171`, `ti,opa362`, `ti,ths8135`. Top-level properties are `compatible`, `ports`, `enable-gpios`, `vdd-supply`. Top-level required properties are `compatible`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: `vdd-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>, Maxime Ripard <mripard@kernel.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/simple-bridge.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/simple-bridge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/snps,dw-mipi-dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/snps,dw-mipi-dsi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/snps,dw-mipi-dsi.yaml` is a Linux devicetree YAML schema for the `Synopsys DesignWare MIPI DSI host controller` MIPI DSI/display bridge binding. This document defines device tree properties for the Synopsys DesignWare MIPI DSI host controller. It doesn't constitute a device tree binding specification by itself but is meant to be referenced by platform-specific device tree bindings. When referenced from platform device tree bindings the properties defined in this document are defined as follows. The platform device tree bindings are responsible for defining whether each property is required or optional. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses no explicit compatible schema and covers 0 compatible tokens: no explicit compatible values. Top-level properties are `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `ports`. Top-level required properties are `clock-names`, `clocks`, `ports`, `reg`; nested required properties found across the schema include `clock-names`, `clocks`, `port@0`, `port@1`, `ports`, `reg`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: `resets`, `reset-names`; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Philippe CORNU <philippe.cornu@foss.st.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `../dsi-controller.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 0 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 8 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level extra properties are intentionally allowed. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/snps,dw-mipi-dsi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/snps,dw-mipi-dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/solomon,ssd2825.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/solomon,ssd2825.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/solomon,ssd2825.yaml` is a Linux devicetree YAML schema for the `Solomon SSD2825 RGB to MIPI-DSI bridge` MIPI DSI/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `solomon,ssd2825`. Top-level properties are `compatible`, `reg`, `reset-gpios`, `dvdd-supply`, `avdd-supply`, `vddio-supply`, `spi-max-frequency`, `spi-cpha`, `spi-cpol`, `clocks`, `solomon,hs-zero-delay-ns`, `solomon,hs-prep-delay-ns`, `ports`. Top-level required properties are `compatible`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `bus-width`. Resource hooks include clocks: `clocks`; resets: `reset-gpios`; regulators/power: `dvdd-supply`, `avdd-supply`, `vddio-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Svyatoslav Ryhel <clamor95@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/spi/spi-peripheral-props.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 13 top-level properties and 17 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/solomon,ssd2825.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/solomon,ssd2825.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/synopsys,dw-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/synopsys,dw-hdmi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/synopsys,dw-hdmi.yaml` is a Linux devicetree YAML schema for the `Common Properties for Synopsys DesignWare HDMI TX Controller` HDMI/display bridge binding. This document defines device tree properties for the Synopsys DesignWare HDMI TX controller (DWC HDMI TX) IP core. It doesn't constitute a full device tree binding specification by itself but is meant to be referenced by device tree bindings for the platform-specific integrations of the DWC HDMI TX. When referenced from platform device tree bindings the properties defined in this document are defined as follows. The platform device tree bindings are responsible for defining whether each property is required or optional. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses no explicit compatible schema and covers 0 compatible tokens: no explicit compatible values. Top-level properties are `reg`, `reg-io-width`, `clocks`, `clock-names`, `ddc-i2c-bus`, `interrupts`. Top-level required properties are none declared at the top level; nested required properties found across the schema include none. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 0 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level extra properties are intentionally allowed. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/synopsys,dw-hdmi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/synopsys,dw-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/thead,th1520-dw-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/thead,th1520-dw-hdmi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/thead,th1520-dw-hdmi.yaml` is a Linux devicetree YAML schema for the `T-Head TH1520 DesignWare HDMI TX Encoder` HDMI/display bridge binding. The HDMI transmitter is a Synopsys DesignWare HDMI TX controller paired with a DesignWare HDMI Gen2 TX PHY. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 1 compatible token: `thead,th1520-dw-hdmi`. Top-level properties are `compatible`, `reg-io-width`, `clocks`, `clock-names`, `resets`, `reset-names`, `ports`. Top-level required properties are `compatible`, `reg`, `reg-io-width`, `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `ports`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `port@0`, `port@1`, `ports`, `reg`, `reg-io-width`, `reset-names`, `resets`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: `resets`, `reset-names`; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Icenowy Zheng <uwu@icenowy.me>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/display/bridge/synopsys,dw-hdmi.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/thead,th1520-dw-hdmi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/thead,th1520-dw-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/thine,thc63lvd1024.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/thine,thc63lvd1024.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/thine,thc63lvd1024.yaml` is a Linux devicetree YAML schema for the `Thine Electronics THC63LVD1024 LVDS Decoder` LVDS/display bridge binding. The THC63LVD1024 is a dual link LVDS receiver designed to convert LVDS streams to parallel data outputs. The chip supports single/dual input/output modes, handling up to two LVDS input streams and up to two digital CMOS/TTL outputs. Single or dual operation mode, output data mapping and DDR output modes are configured through input signals and the chip does not expose any control bus. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `thine,thc63lvd1024`. Top-level properties are `compatible`, `ports`, `oe-gpios`, `powerdown-gpios`, `vcc-supply`. Top-level required properties are `compatible`, `ports`, `vcc-supply`; nested required properties found across the schema include `compatible`, `port@0`, `port@2`, `ports`, `vcc-supply`. Graph integration is expressed through `port@0`, `port@1`, `port@2`, `port@3`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: `vcc-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Jacopo Mondi <jacopo+renesas@jmondi.org>, Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/thine,thc63lvd1024.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/thine,thc63lvd1024.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,dlpc3433.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,dlpc3433.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,dlpc3433.yaml` is a Linux devicetree YAML schema for the `TI DLPC3433 MIPI DSI to DMD bridge` MIPI DSI/display bridge binding. TI DLPC3433 is a MIPI DSI based display controller bridge for processing high resolution DMD based projectors. It has a flexible configuration of MIPI DSI and DPI signal input that produces a DMD output in RGB565, RGB666, RGB888 formats. It supports upto 720p resolution with 60 and 120 Hz refresh rates. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `ti,dlpc3433`. Top-level properties are `compatible`, `reg`, `enable-gpios`, `vcc_intf-supply`, `vcc_flsh-supply`, `ports`. Top-level required properties are `compatible`, `reg`, `enable-gpios`, `ports`; nested required properties found across the schema include `compatible`, `enable-gpios`, `port@0`, `port@1`, `ports`, `reg`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: none; resets: none; regulators/power: `vcc_intf-supply`, `vcc_flsh-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Jagan Teki <jagan@amarulasolutions.com>, Christopher Vollo <chris@renewoutreach.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ti,dlpc3433.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,dlpc3433.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,sn65dsi83.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,sn65dsi83.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,sn65dsi83.yaml` is a Linux devicetree YAML schema for the `SN65DSI83 and SN65DSI84 DSI to LVDS bridge chip` MIPI DSI/display bridge binding. Texas Instruments SN65DSI83 1x Single-link MIPI DSI to 1x Single-link LVDS https://www.ti.com/lit/gpn/sn65dsi83 Texas Instruments SN65DSI84 1x Single-link MIPI DSI to 1x Dual-link or 2x Single-link LVDS https://www.ti.com/lit/gpn/sn65dsi84 It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `ti,sn65dsi83`, `ti,sn65dsi84`. Top-level properties are `compatible`, `reg`, `enable-gpios`, `vcc-supply`, `interrupts`, `ports`. Top-level required properties are `compatible`, `reg`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@2`, `ports`, `reg`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `port@2`, `port@3`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: none; resets: none; regulators/power: `vcc-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Marek Vasut <marex@denx.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `#/$defs/lvds-port`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 15 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ti,sn65dsi83.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,sn65dsi83.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,sn65dsi86.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,sn65dsi86.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,sn65dsi86.yaml` is a Linux devicetree YAML schema for the `SN65DSI86 DSI to eDP bridge chip` MIPI DSI/display bridge binding. The Texas Instruments SN65DSI86 bridge takes MIPI DSI in and outputs eDP. https://www.ti.com/general/docs/lit/getliterature.tsp?genericPartNumber=sn65dsi86&fileType=pdf It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `ti,sn65dsi86`. Top-level properties are `compatible`, `reg`, `enable-gpios`, `suspend-gpios`, `no-hpd`, `vccio-supply`, `vpll-supply`, `vcca-supply`, `vcc-supply`, `interrupts`, `clocks`, `clock-names`, `gpio-controller`, `#gpio-cells`, `#pwm-cells`, `aux-bus`, `ports`. Top-level required properties are `compatible`, `reg`, `vccio-supply`, `vpll-supply`, `vcca-supply`, `vcc-supply`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`, `reg`, `vcc-supply`, `vcca-supply`, `vccio-supply`, `vpll-supply`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: `vccio-supply`, `vpll-supply`, `vcca-supply`, `vcc-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Douglas Anderson <dianders@chromium.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/display/dp-aux-bus.yaml#`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 17 top-level properties and 22 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ti,sn65dsi86.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,sn65dsi86.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,tdp158.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,tdp158.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,tdp158.yaml` is a Linux devicetree YAML schema for the `TI TDP158 HDMI to TMDS Redriver` HDMI/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `ti,tdp158`. Top-level properties are `compatible`, `reg`, `enable-gpios`, `vcc-supply`, `vdd-supply`, `ports`. Top-level required properties are `compatible`, `vcc-supply`, `vdd-supply`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`, `vcc-supply`, `vdd-supply`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: `vcc-supply`, `vdd-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Arnaud Vrac <avrac@freebox.fr>, Pierre-Hugues Husson <phhusson@freebox.fr>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 0 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 8 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ti,tdp158.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,tdp158.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,tfp410.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,tfp410.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,tfp410.yaml` is a Linux devicetree YAML schema for the `TFP410 DPI to DVI encoder` display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `ti,tfp410`. Top-level properties are `compatible`, `reg`, `powerdown-gpios`, `ti,deskew`, `ports`. Top-level required properties are `compatible`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`, `reg`, `ti,deskew`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `bus-width`. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Tomi Valkeinen <tomi.valkeinen@ti.com>, Jyri Sarha <jsarha@ti.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32`. Pattern properties are none; top-level composition/conditional keys are `if`, `then`, `else`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ti,tfp410.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ti,tfp410.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358762.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358762.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358762.yaml` is a Linux devicetree YAML schema for the `Toshiba TC358762 MIPI DSI to MIPI DPI bridge` MIPI DSI/display bridge binding. The TC358762 is bridge device which converts MIPI DSI to MIPI DPI. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 1 compatible token: `toshiba,tc358762`. Top-level properties are `compatible`, `reg`, `reset-gpios`, `vddc-supply`, `ports`. Top-level required properties are `compatible`, `reg`, `vddc-supply`, `ports`; nested required properties found across the schema include `compatible`, `port@1`, `ports`, `reg`, `vddc-supply`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vddc-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Marek Vasut <marex@denx.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 7 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/toshiba,tc358762.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358762.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358764.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358764.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358764.yaml` is a Linux devicetree YAML schema for the `Toshiba TC358764 MIPI-DSI to LVDS bridge` MIPI DSI/display bridge binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `toshiba,tc358764`. Top-level properties are `compatible`, `reg`, `reset-gpios`, `vddc-supply`, `vddio-supply`, `vddlvds-supply`, `ports`. Top-level required properties are `compatible`, `reg`, `reset-gpios`, `vddc-supply`, `vddio-supply`, `vddlvds-supply`, `ports`; nested required properties found across the schema include `compatible`, `port@1`, `ports`, `reg`, `reset-gpios`, `vddc-supply`, `vddio-supply`, `vddlvds-supply`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vddc-supply`, `vddio-supply`, `vddlvds-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Andrzej Hajda <andrzej.hajda@intel.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/toshiba,tc358764.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358764.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358767.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358767.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358767.yaml` is a Linux devicetree YAML schema for the `Toshiba TC358767/TC358867/TC9595 DSI/DPI/eDP bridge` MIPI DSI/display bridge binding. The TC358767/TC358867/TC9595 is bridge device which converts DSI/DPI to eDP/DP . It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 3 compatible tokens: `toshiba,tc358867`, `toshiba,tc9595`, `toshiba,tc358767`. Top-level properties are `compatible`, `reg`, `clock-names`, `clocks`, `shutdown-gpios`, `reset-gpios`, `interrupts`, `toshiba,hpd-pin`, `ports`. Top-level required properties are `compatible`, `reg`, `clock-names`, `clocks`, `ports`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `port@0`, `port@1`, `ports`, `reg`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `port@2`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: `clock-names`, `clocks`; resets: `reset-gpios`; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Andrey Gusakov <andrey.gusakov@cogentembedded.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint8-array`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 9 top-level properties and 15 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/toshiba,tc358767.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358767.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358768.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358768.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358768.yaml` is a Linux devicetree YAML schema for the `Toschiba TC358768/TC358778 Parallel RGB to MIPI DSI bridge` MIPI DSI/display bridge binding. The TC358768/TC358778 is bridge device which converts RGB to DSI. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `toshiba,tc358768`, `toshiba,tc358778`. Top-level properties are `compatible`, `reg`, `reset-gpios`, `vddc-supply`, `vddmipi-supply`, `vddio-supply`, `clocks`, `clock-names`, `ports`. Top-level required properties are `compatible`, `reg`, `vddc-supply`, `vddmipi-supply`, `vddio-supply`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`, `reg`, `vddc-supply`, `vddio-supply`, `vddmipi-supply`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `bus-width`. Resource hooks include clocks: `clocks`, `clock-names`; resets: `reset-gpios`; regulators/power: `vddc-supply`, `vddmipi-supply`, `vddio-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Peter Ujfalusi <peter.ujfalusi@ti.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `../dsi-controller.yaml#`, `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 9 top-level properties and 14 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/toshiba,tc358768.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358768.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358775.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358775.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358775.yaml` is a Linux devicetree YAML schema for the `Toshiba TC358775 DSI to LVDS bridge` MIPI DSI/display bridge binding. This binding supports DSI to LVDS bridges TC358765 and TC358775 MIPI DSI-RX Data 4-lane, CLK 1-lane with data rates up to 800 Mbps/lane. Video frame size: Up to 1600x1200 24-bit/pixel resolution for single-link LVDS display panel limited by 135 MHz LVDS speed Up to WUXGA (1920x1200 24-bit pixels) resolution for dual-link LVDS display panel, limited by 270 MHz LVDS speed. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `toshiba,tc358765`, `toshiba,tc358775`. Top-level properties are `compatible`, `reg`, `vdd-supply`, `vddio-supply`, `stby-gpios`, `reset-gpios`, `ports`. Top-level required properties are `compatible`, `reg`, `vdd-supply`, `vddio-supply`, `reset-gpios`, `ports`; nested required properties found across the schema include `compatible`, `port@0`, `port@1`, `ports`, `reg`, `reset-gpios`, `vdd-supply`, `vddio-supply`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `port@2`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: `vdd-supply`, `vddio-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Vinay Simha BN <simhavcs@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 12 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/toshiba,tc358775.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/toshiba,tc358775.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/waveshare,dsi2dpi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/waveshare,dsi2dpi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/waveshare,dsi2dpi.yaml` is a Linux devicetree YAML schema for the `Waveshare MIPI-DSI to DPI Converter bridge` MIPI DSI/display bridge binding. Waveshare bridge board is part of Waveshare panel which converts DSI to DPI. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `waveshare,dsi2dpi`. Top-level properties are `compatible`, `reg`, `power-supply`, `ports`. Top-level required properties are `compatible`, `reg`, `ports`, `power-supply`; nested required properties found across the schema include `compatible`, `data-lanes`, `port@0`, `port@1`, `ports`, `power-supply`, `reg`. Graph integration is expressed through `endpoint`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include `data-lanes`. Resource hooks include clocks: none; resets: none; regulators/power: `power-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Joseph Guo <qijian.guo@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/media/video-interfaces.yaml#`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 8 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/waveshare,dsi2dpi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/waveshare,dsi2dpi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/analog-tv-connector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/analog-tv-connector.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/analog-tv-connector.yaml` is a Linux devicetree YAML schema for the `Analog TV Connector` display connector binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `composite-video-connector`, `svideo-connector`. Top-level properties are `compatible`, `label`, `sdtv-standards`, `port`. Top-level required properties are `compatible`, `port`; nested required properties found across the schema include `compatible`, `port`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <Laurent.pinchart@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/uint32`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 4 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/connector/analog-tv-connector.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/analog-tv-connector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/dp-connector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/dp-connector.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/dp-connector.yaml` is a Linux devicetree YAML schema for the `DisplayPort Connector` display connector binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `dp-connector`. Top-level properties are `compatible`, `label`, `type`, `hpd-gpios`, `dp-pwr-supply`, `port`, `ports`. Top-level required properties are `compatible`, `type`; nested required properties found across the schema include `compatible`, `port`, `port@0`, `port@1`, `ports`, `type`. Graph integration is expressed through `port`, `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: `dp-pwr-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Tomi Valkeinen <tomi.valkeinen@ti.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are `oneOf`; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/connector/dp-connector.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/dp-connector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/dvi-connector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/dvi-connector.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/dvi-connector.yaml` is a Linux devicetree YAML schema for the `DVI Connector` display connector binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `dvi-connector`. Top-level properties are `compatible`, `label`, `hpd-gpios`, `ddc-i2c-bus`, `analog`, `digital`, `dual-link`, `port`. Top-level required properties are `compatible`, `port`; nested required properties found across the schema include `analog`, `compatible`, `digital`, `port`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <Laurent.pinchart@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are `anyOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 8 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/connector/dvi-connector.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/dvi-connector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/hdmi-connector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/hdmi-connector.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/hdmi-connector.yaml` is a Linux devicetree YAML schema for the `HDMI Connector` display connector binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `hdmi-connector`. Top-level properties are `compatible`, `type`, `label`, `hpd-gpios`, `ddc-i2c-bus`, `ddc-en-gpios`, `hdmi-pwr-supply`, `port`. Top-level required properties are `compatible`, `port`, `type`; nested required properties found across the schema include `compatible`, `port`, `type`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: `hdmi-pwr-supply`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <Laurent.pinchart@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 8 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/connector/hdmi-connector.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/hdmi-connector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/vga-connector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/vga-connector.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/vga-connector.yaml` is a Linux devicetree YAML schema for the `VGA Connector` display connector binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `vga-connector`. Top-level properties are `compatible`, `label`, `ddc-i2c-bus`, `port`. Top-level required properties are `compatible`, `port`; nested required properties found across the schema include `compatible`, `port`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <Laurent.pinchart@ideasonboard.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 4 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/connector/vga-connector.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/connector/vga-connector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/dp-aux-bus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/dp-aux-bus.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/dp-aux-bus.yaml` is a Linux devicetree YAML schema for the `DisplayPort AUX bus` DisplayPort AUX bus binding. DisplayPort controllers provide a control channel to the sinks that are hooked up to them. This is the DP AUX bus. Over the DP AUX bus we can query properties about a sink and also configure it. In particular, DP sinks support DDC over DP AUX which allows tunneling a standard I2C DDC connection over the AUX channel. To model this relationship, DP sinks should be placed as children of the DP controller under the "aux-bus" node. At the moment, this binding only handles the eDP case. It is possible it will be extended in the future to handle the DP case. For DP, presumably a connector would be listed under the DP AUX bus instead of a panel. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses no explicit compatible schema and covers 0 compatible tokens: no explicit compatible values. Top-level properties are `$nodename`, `panel`. Top-level required properties are `panel`; nested required properties found across the schema include `panel`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Douglas Anderson <dianders@chromium.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `panel/panel-common.yaml#`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 0 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 2 top-level properties and 2 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/dp-aux-bus.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/dp-aux-bus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/dsi-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/dsi-controller.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/dsi-controller.yaml` is a Linux devicetree YAML schema for the `Common Properties for DSI Display Panels` generic MIPI DSI controller binding. This document defines device tree properties common to DSI, Display Serial Interface controllers and attached panels. It doesn't constitute a device tree binding specification by itself but is meant to be referenced by device tree bindings. When referenced from panel device tree bindings the properties defined in this document are defined as follows. The panel device tree bindings are responsible for defining whether each property is required or optional. Notice: this binding concerns DSI panels connected directly to a master without any intermediate port graph to the panel. Each DSI master can control one to four virtual channels to one panel. Each virtual channel should have a node "panel" for their virtual channel with their reg-property set to... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses no explicit compatible schema and covers 0 compatible tokens: no explicit compatible values. Top-level properties are `$nodename`, `clock-master`, `#address-cells`, `#size-cells`. Top-level required properties are none declared at the top level; nested required properties found across the schema include `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clock-master`; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are `^(panel|bridge)@[0-3]$`; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level extra properties are intentionally allowed. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/dsi-controller.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/dsi-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/elgin,jg10309-01.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/elgin,jg10309-01.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/elgin,jg10309-01.yaml` is a Linux devicetree YAML schema for the `Elgin JG10309-01 SPI-controlled display` display controller binding. The Elgin JG10309-01 SPI-controlled display is used on the RV1108-Elgin-r1 board and is a custom display. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `elgin,jg10309-01`. Top-level properties are `compatible`, `reg`, `spi-max-frequency`, `spi-cpha`, `spi-cpol`. Top-level required properties are `compatible`, `reg`, `spi-cpha`, `spi-cpol`; nested required properties found across the schema include `compatible`, `reg`, `spi-cpha`, `spi-cpol`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Fabio Estevam <festevam@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 5 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/elgin,jg10309-01.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/elgin,jg10309-01.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/faraday,tve200.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/faraday,tve200.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/faraday,tve200.yaml` is a Linux devicetree YAML schema for the `Faraday TV Encoder TVE200` display controller binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 2 compatible tokens: `faraday,tve200`, `cortina,gemini-tvc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `resets`, `port`. Top-level required properties are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clock-names`, `clocks`; resets: `resets`; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 7 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/faraday,tve200.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/faraday,tve200.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,lcdif.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,lcdif.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,lcdif.yaml` is a Linux devicetree YAML schema for the `Freescale/NXP i.MX LCD Interface (LCDIF)` display controller binding. (e)LCDIF display controller found in the Freescale/NXP i.MX SoCs. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 12 compatible tokens: `fsl,imx23-lcdif`, `fsl,imx28-lcdif`, `fsl,imx6sx-lcdif`, `fsl,imx8mp-lcdif`, `fsl,imx93-lcdif`, `fsl,imx6sl-lcdif`, `fsl,imx6sll-lcdif`, `fsl,imx6ul-lcdif`, `fsl,imx7d-lcdif`, `fsl,imx8mm-lcdif`, `fsl,imx8mn-lcdif`, `fsl,imx8mq-lcdif`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `dmas`, `dma-names`, `interrupts`, `power-domains`, `port`, `display`, `display0`, `lcd-supply`. Top-level required properties are `compatible`, `reg`, `clocks`, `interrupts`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `port`, `power-domains`, `reg`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: `power-domains`, `lcd-supply`; IRQ/DMA-related: `dmas`, `dma-names`, `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Marek Vasut <marex@denx.de>, Stefan Agner <stefan@agner.ch>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`, `panel/panel-common.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 12 top-level properties and 12 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/fsl,lcdif.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,lcdif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,ls1021a-dcu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,ls1021a-dcu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,ls1021a-dcu.yaml` is a Linux devicetree YAML schema for the `Freescale DCU DRM Driver` display controller binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `fsl,ls1021a-dcu`, `fsl,vf610-dcu`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `big-endian`, `port`, `fsl,tcon`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `reg`. Graph integration is expressed through `endpoint`, `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`, `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/fsl,ls1021a-dcu.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,ls1021a-dcu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,vf610-tcon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,vf610-tcon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,vf610-tcon.yaml` is a Linux devicetree YAML schema for the `Freescale TCON` display controller binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,vf610-tcon`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 4 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/fsl,vf610-tcon.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/fsl,vf610-tcon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/google,goldfish-fb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/google,goldfish-fb.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/google,goldfish-fb.yaml` is a Linux devicetree YAML schema for the `Android Goldfish Framebuffer` display controller binding. Android Goldfish framebuffer device used by Android emulator. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `google,goldfish-fb`. Top-level properties are `compatible`, `reg`, `interrupts`. Top-level required properties are `compatible`, `reg`, `interrupts`; nested required properties found across the schema include `compatible`, `interrupts`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Kuan-Wei Chiu <visitorckw@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/google,goldfish-fb.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/google,goldfish-fb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/himax,hx8357.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/himax,hx8357.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/himax,hx8357.yaml` is a Linux devicetree YAML schema for the `Himax HX8357D display panel` display panel binding. Display panels using a Himax HX8357D controller in SPI mode, such as the Adafruit 3.5" TFT for Raspberry Pi. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 5 compatible tokens: `adafruit,yx350hv15`, `himax,hx8357b`, `himax,hx8357`, `himax,hx8369a`, `himax,hx8369`. Top-level properties are `compatible`, `reg`, `dc-gpios`, `rotation`, `backlight`, `im-gpios`, `reset-gpios`, `spi-cpha`, `spi-cpol`. Top-level required properties are `compatible`, `reg`; nested required properties found across the schema include `compatible`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 9 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/himax,hx8357.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/himax,hx8357.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ilitek,ili9486.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ilitek,ili9486.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ilitek,ili9486.yaml` is a Linux devicetree YAML schema for the `Ilitek ILI9486 display panels` display panel binding. This binding is for display panels using an Ilitek ILI9486 controller in SPI mode. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses ordered `items` sequence and covers 3 compatible tokens: `waveshare,rpi-lcd-35`, `ozzmaker,piscreen`, `ilitek,ili9486`. Top-level properties are `compatible`, `spi-max-frequency`, `dc-gpios`, `backlight`, `reg`, `reset-gpios`, `rotation`. Top-level required properties are `compatible`, `reg`, `dc-gpios`, `reset-gpios`; nested required properties found across the schema include `compatible`, `dc-gpios`, `reg`, `reset-gpios`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Kamlesh Gurudasani <kamlesh.gurudasani@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `panel/panel-common.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 7 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/ilitek,ili9486.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ilitek,ili9486.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-display-subsystem.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-display-subsystem.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-display-subsystem.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX DRM master device` NXP/Freescale i.MX display block binding. The freescale i.MX DRM master device is a virtual device needed to list all IPU or other display interface nodes that comprise the graphics subsystem. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx-display-subsystem`. Top-level properties are `compatible`, `ports`. Top-level required properties are `compatible`; nested required properties found across the schema include `compatible`. Graph integration is expressed through `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/types.yaml#/definitions/phandle-array`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 2 top-level properties and 2 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx-display-subsystem.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-display-subsystem.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-lcdc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-lcdc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-lcdc.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX LCD Controller, found on i.MX1, i.MX21, i.MX25 and i.MX27` NXP/Freescale i.MX display block binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 3 accepted compatible forms and covers 6 compatible tokens: `fsl,imx1-fb`, `fsl,imx21-fb`, `fsl,imx25-fb`, `fsl,imx27-fb`, `fsl,imx25-lcdc`, `fsl,imx21-lcdc`. Top-level properties are `compatible`, `clocks`, `clock-names`, `port`, `display`, `interrupts`, `reg`, `lcd-supply`, `fsl,dmacr`, `fsl,lpccr`, `fsl,lscr1`. Top-level required properties are `compatible`, `clocks`, `clock-names`, `interrupts`, `reg`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `display`, `interrupts`, `port`, `reg`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: `lcd-supply`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Sascha Hauer <s.hauer@pengutronix.de>, Pengutronix Kernel Team <kernel@pengutronix.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 11 top-level properties and 11 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx-lcdc.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-lcdc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-parallel-display.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-parallel-display.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-parallel-display.yaml` is a Linux devicetree YAML schema for the `Parallel display support` NXP/Freescale i.MX display block binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx-parallel-display`. Top-level properties are `compatible`, `interface-pix-fmt`, `ddc`, `#address-cells`, `#size-cells`, `port@0`, `port@1`. Top-level required properties are `compatible`; nested required properties found across the schema include `compatible`. Graph integration is expressed through `port@0`, `port@1`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 7 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx-parallel-display.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx-parallel-display.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6-hdmi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6-hdmi.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX6 DWC HDMI TX Encoder` NXP/Freescale i.MX display block binding. The HDMI transmitter is a Synopsys DesignWare HDMI 1.4 TX controller IP with a companion PHY IP. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `fsl,imx6dl-hdmi`, `fsl,imx6q-hdmi`. Top-level properties are `compatible`, `reg-io-width`, `clocks`, `clock-names`, `gpr`, `ports`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`, `gpr`, `interrupts`, `ports`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `gpr`, `interrupts`, `port@0`, `port@1`, `port@2`, `port@3`, `ports`, `reg`. Graph integration is expressed through `port@0`, `port@1`, `port@2`, `port@3`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Philipp Zabel <p.zabel@pengutronix.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `../bridge/synopsys,dw-hdmi.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx6-hdmi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6q-ipu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6q-ipu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6q-ipu.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX IPUv3` NXP/Freescale i.MX display block binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 4 compatible tokens: `fsl,imx51-ipu`, `fsl,imx53-ipu`, `fsl,imx6q-ipu`, `fsl,imx6qp-ipu`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `#address-cells`, `#size-cells`, `fsl,prg`, `port@0`, `port@1`, `port@2`, `port@3`. Top-level required properties are `compatible`, `reg`, `interrupts`, `resets`; nested required properties found across the schema include `compatible`, `interrupts`, `reg`, `resets`. Graph integration is expressed through `port@0`, `port@1`, `port@2`, `port@3`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: `resets`; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/$defs/port-base`, `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 13 top-level properties and 13 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx6q-ipu.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6q-ipu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6q-ldb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6q-ldb.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6q-ldb.yaml` is a Linux devicetree YAML schema for the `Freescale LVDS Display Bridge (ldb)` NXP/Freescale i.MX display block binding. The LVDS Display Bridge device tree node contains up to two lvds-channel nodes describing each of the two LVDS encoder channels of the bridge. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 2 compatible tokens: `fsl,imx53-ldb`, `fsl,imx6q-ldb`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `gpr`, `clocks`, `clock-names`, `fsl,dual-channel`. Top-level required properties are `compatible`, `gpr`, `clocks`, `clock-names`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `gpr`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/display/panel/display-timings.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Pattern properties are `^lvds-channel@[0-1]$`; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 12 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx6q-ldb.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6q-ldb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6qp-pre.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6qp-pre.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6qp-pre.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX PRE (Prefetch Resolve Engine)` NXP/Freescale i.MX display block binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx6qp-pre`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `fsl,iram`. Top-level required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx6qp-pre.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6qp-pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6qp-prg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6qp-prg.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6qp-prg.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX PRG (Prefetch Resolve Gasket)` NXP/Freescale i.MX display block binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx6qp-prg`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `fsl,pres`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/types.yaml#/definitions/phandle-array`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 5 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx6qp-prg.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx6qp-prg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pai.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pai.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pai.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8MP HDMI Parallel Audio Interface` NXP/Freescale i.MX display block binding. The HDMI TX Parallel Audio Interface (HTX_PAI) is a bridge between the Audio Subsystem to the HDMI TX Controller. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8mp-hdmi-pai`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `port`. Top-level required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `port`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `port`, `power-domains`, `reg`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: `power-domains`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Shengjiu Wang <shengjiu.wang@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 7 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pai.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pai.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pvi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pvi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pvi.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8MP HDMI Parallel Video Interface` NXP/Freescale i.MX display block binding. The HDMI parallel video interface is a timing and sync generator block in the i.MX8MP SoC, that sits between the video source and the HDMI TX controller. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8mp-hdmi-pvi`. Top-level properties are `compatible`, `reg`, `interrupts`, `power-domains`, `ports`. Top-level required properties are `compatible`, `reg`, `interrupts`, `power-domains`, `ports`; nested required properties found across the schema include `compatible`, `interrupts`, `port@0`, `port@1`, `ports`, `power-domains`, `reg`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: `power-domains`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Lucas Stach <l.stach@pengutronix.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 7 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pvi.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8mp-hdmi-pvi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-axi-performance-counter.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-axi-performance-counter.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-axi-performance-counter.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller AXI Performance Counter` NXP/Freescale i.MX display block binding. Performance counters are provided to allow measurement of average bandwidth and latency during operation. The following features are supported: * Manual and timer controlled measurement mode. * Measurement counters: - GLOBAL_COUNTER for overall measurement time - BUSY_COUNTER for number of data bus busy cycles - DATA_COUNTER for number of data transfer cycles - TRANSFER_COUNTER for number of transfers - ADDRBUSY_COUNTER for number of address bus busy cycles - LATENCY_COUNTER for average latency * Counter overflow detection. * Outstanding Transfer Counters (OTC) which are used for latency measurement have to run immediately after reset, but can be disabled by software when there is no need for latency measurement. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-axi-performance-counter`. Top-level properties are `compatible`, `reg`, `clocks`. Top-level required properties are `compatible`, `reg`, `clocks`; nested required properties found across the schema include `clocks`, `compatible`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-axi-performance-counter.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-axi-performance-counter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blit-engine.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blit-engine.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blit-engine.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Blit Engine` NXP/Freescale i.MX display block binding. A blit operation (block based image transfer) reads up to 3 source images from memory and computes one destination image from it, which is written back to memory. The following basic operations are supported: * Buffer Fill Fills a buffer with constant color * Buffer Copy Copies one source to a destination buffer. * Image Blend Combines two source images by a blending equation and writes result to destination (which can be one of the sources). * Image Rop2/3 Combines up to three source images by a logical equation (raster operation) and writes result to destination (which can be one of the sources). * Image Flip Mirrors the source image in horizontal and/or vertical direction. * Format Convert Convert between the supported color and buffer formats.... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-blit-engine`. Top-level properties are `compatible`, `reg`, `reg-names`, `#address-cells`, `#size-cells`, `ranges`. Top-level required properties are `compatible`, `reg`, `reg-names`, `#address-cells`, `#size-cells`, `ranges`; nested required properties found across the schema include `#address-cells`, `#size-cells`, `compatible`, `ranges`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are `^blitblend@[0-9a-f]+$`, `^clut@[0-9a-f]+$`, `^fetchdecode@[0-9a-f]+$`, `^fetcheco@[0-9a-f]+$`, `^fetchwarp@[0-9a-f]+$`, `^filter@[0-9a-f]+$`, `^hscaler@[0-9a-f]+$`, `^matrix@[0-9a-f]+$`, and 3 more; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blit-engine.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blit-engine.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blitblend.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blitblend.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blitblend.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Blit Blend Unit` NXP/Freescale i.MX display block binding. Combines two input frames to a single output frame, all frames having the same dimension. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-blitblend`. Top-level properties are `compatible`, `reg`, `reg-names`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blitblend.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-blitblend.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-clut.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-clut.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-clut.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Color Lookup Table` NXP/Freescale i.MX display block binding. The unit implements 3 look-up tables with 256 x 10 bit entries each. These can be used for different kinds of applications. From 10-bit input values only upper 8 bits are used. The unit supports color lookup, index lookup, dithering and alpha masking. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-clut`. Top-level properties are `compatible`, `reg`, `reg-names`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-clut.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-clut.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-command-sequencer.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-command-sequencer.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-command-sequencer.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Command Sequencer` NXP/Freescale i.MX display block binding. The Command Sequencer is designed to autonomously process command lists. By that it can load setups into the DC configuration and synchronize to hardware events. This releases a system's CPU from workload, because it does not need to wait for certain events. Also it simplifies SW architecture, because no interrupt handlers are required. Setups are read via AXI bus, while write access to configuration registers occurs directly via an internal bus. This saves bandwidth for the AXI interconnect and improves the system architecture in terms of safety aspects. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-command-sequencer`. Top-level properties are `compatible`, `reg`, `clocks`, `interrupts`, `interrupt-names`, `sram`. Top-level required properties are `compatible`, `reg`, `clocks`, `interrupts`, `interrupt-names`; nested required properties found across the schema include `clocks`, `compatible`, `interrupt-names`, `interrupts`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`, `interrupt-names`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-command-sequencer.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-command-sequencer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-constframe.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-constframe.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-constframe.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Constant Frame` NXP/Freescale i.MX display block binding. The Constant Frame unit is used instead of a Fetch unit where generation of constant color frames only is sufficient. This is the case for the background planes of content and safety streams in a Display Controller. The color can be setup to any RGBA value. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-constframe`. Top-level properties are `compatible`, `reg`, `reg-names`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-constframe.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-constframe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-display-engine.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-display-engine.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-display-engine.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Display Engine` NXP/Freescale i.MX display block binding. All Processing Units that operate in a display clock domain. Pixel pipeline is driven by a video timing and cannot be stalled. Implements all display specific processing. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-display-engine`. Top-level properties are `compatible`, `reg`, `reg-names`, `resets`, `interrupts`, `interrupt-names`, `power-domains`, `#address-cells`, `#size-cells`, `ranges`. Top-level required properties are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `power-domains`, `#address-cells`, `#size-cells`, `ranges`; nested required properties found across the schema include `#address-cells`, `#size-cells`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `ranges`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `resets`; regulators/power: `power-domains`; IRQ/DMA-related: `interrupts`, `interrupt-names`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are `^dither@[0-9a-f]+$`, `^framegen@[0-9a-f]+$`, `^gammacor@[0-9a-f]+$`, `^matrix@[0-9a-f]+$`, `^signature@[0-9a-f]+$`, `^tcon@[0-9a-f]+$`; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 10 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-display-engine.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-display-engine.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-dither.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-dither.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-dither.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Dither Unit` NXP/Freescale i.MX display block binding. The unit can increase the physical color resolution of a display from 5, 6, 7 or 8 bits per RGB channel to a virtual resolution of 10 bits. The physical resolution can be set individually for each channel. The resolution is increased by mixing the two physical colors that are nearest to the virtual color code in a variable ratio either by time (temporal dithering) or by position (spatial dithering). An optimized algorithm for temporal dithering minimizes noise artifacts on the output image. The dither operation can be individually enabled or disabled for each pixel using the alpha input bit. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-dither`. Top-level properties are `compatible`, `reg`. Top-level required properties are `compatible`, `reg`; nested required properties found across the schema include `compatible`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 2 top-level properties and 2 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-dither.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-dither.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-extdst.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-extdst.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-extdst.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller External Destination Interface` NXP/Freescale i.MX display block binding. The External Destination unit is the interface between the internal pixel processing pipeline of the Pixel Engine, which is 30-bit RGB plus 8-bit Alpha, and a Display Engine. It comprises the following built-in Gamma apply function. +------X-----------------------+ | | ExtDst Unit | | V | | +-------+ | | | Gamma | | | +-------+ | | | | | V + +------X-----------------------+ The output format is 24-bit RGB plus 1-bit Alpha. Conversion from 10 to 8 bits is done by LSBit truncation. Alpha output bit is 1 for input 255, 0 otherwise. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-extdst`. Top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`. Top-level required properties are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`; nested required properties found across the schema include `compatible`, `interrupt-names`, `interrupts`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`, `interrupt-names`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 5 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-extdst.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-extdst.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-fetchunit.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-fetchunit.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-fetchunit.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Fetch Unit` NXP/Freescale i.MX display block binding. The Fetch Unit is the interface between the AXI bus for source buffer access and the internal pixel processing pipeline, which is 30-bit RGB plus 8-bit Alpha. It is used to generate foreground planes in Display Controllers and source planes in Blit Engines, and comprises the following built-in functions to convert a wide range of frame buffer types. +---------X-----------------------------------------+ | | Fetch Unit | | V | | +---------+ | | | | | | | Decode | Decompression [Decode] | | | | | | +---------+ | | | | | V | | +---------+ | | | Clip & | Clip Window [All] | | | Overlay | Plane composition [Layer, Warp] | | | | | | +---------+ | | | | | V | | +---------+ | | | Re- | Flip/Rotate/Repl./Drop [All] | X--> | sample | Perspective/Affine warpi... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 4 compatible tokens: `fsl,imx8qxp-dc-fetchdecode`, `fsl,imx8qxp-dc-fetcheco`, `fsl,imx8qxp-dc-fetchlayer`, `fsl,imx8qxp-dc-fetchwarp`. Top-level properties are `compatible`, `reg`, `reg-names`, `fsl,prg`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 4 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-fetchunit.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-fetchunit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-filter.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-filter.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-filter.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Filter Unit` NXP/Freescale i.MX display block binding. 5x5 FIR filter with 25 programmable coefficients. Typical applications are image blurring, sharpening or support for edge detection algorithms. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-filter`. Top-level properties are `compatible`, `reg`, `reg-names`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-filter.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-filter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-framegen.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-framegen.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-framegen.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Frame Generator` NXP/Freescale i.MX display block binding. The Frame Generator (FrameGen) module generates a programmable video timing and optionally allows to synchronize the generated video timing to external synchronization signals. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-framegen`. Top-level properties are `compatible`, `reg`, `clocks`, `interrupts`, `interrupt-names`. Top-level required properties are `compatible`, `reg`, `clocks`, `interrupts`, `interrupt-names`; nested required properties found across the schema include `clocks`, `compatible`, `interrupt-names`, `interrupts`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`, `interrupt-names`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 5 top-level properties and 5 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-framegen.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-framegen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-gammacor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-gammacor.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-gammacor.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Gamma Correction Unit` NXP/Freescale i.MX display block binding. The unit supports non-linear color transformation. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-gammacor`. Top-level properties are `compatible`, `reg`. Top-level required properties are `compatible`, `reg`; nested required properties found across the schema include `compatible`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 2 top-level properties and 2 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-gammacor.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-gammacor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-layerblend.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-layerblend.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-layerblend.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Layer Blend Unit` NXP/Freescale i.MX display block binding. Combines two input frames to a single output frame. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-layerblend`. Top-level properties are `compatible`, `reg`, `reg-names`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-layerblend.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-layerblend.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-matrix.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-matrix.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-matrix.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Color Matrix` NXP/Freescale i.MX display block binding. The unit supports linear color transformation, alpha pre-multiply and alpha masking. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-matrix`. Top-level properties are `compatible`, `reg`, `reg-names`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-matrix.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-matrix.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-pixel-engine.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-pixel-engine.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-pixel-engine.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Pixel Engine` NXP/Freescale i.MX display block binding. All Processing Units that operate in the AXI bus clock domain. Pixel pipelines have the ability to stall when a destination is busy. Implements all communication to memory resources and most of the image processing functions. Interconnection of Processing Units is re-configurable. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-pixel-engine`. Top-level properties are `compatible`, `reg`, `clocks`, `#address-cells`, `#size-cells`, `ranges`. Top-level required properties are `compatible`, `reg`, `clocks`, `#address-cells`, `#size-cells`, `ranges`; nested required properties found across the schema include `#address-cells`, `#size-cells`, `clocks`, `compatible`, `ranges`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are `^blit-engine@[0-9a-f]+$`, `^constframe@[0-9a-f]+$`, `^extdst@[0-9a-f]+$`, `^fetchdecode@[0-9a-f]+$`, `^fetcheco@[0-9a-f]+$`, `^fetchlayer@[0-9a-f]+$`, `^fetchwarp@[0-9a-f]+$`, `^hscaler@[0-9a-f]+$`, and 4 more; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-pixel-engine.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-pixel-engine.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-rop.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-rop.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-rop.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Raster Operation Unit` NXP/Freescale i.MX display block binding. The unit can combine up to three input frames to a single output frame, all having the same dimension. The unit supports logic operations, arithmetic operations and packing. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-rop`. Top-level properties are `compatible`, `reg`, `reg-names`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-rop.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-rop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-safety.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-safety.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-safety.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Safety Unit` NXP/Freescale i.MX display block binding. The unit allows corresponding processing units to be configured in a path leading to multiple endpoints. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-safety`. Top-level properties are `compatible`, `reg`. Top-level required properties are `compatible`, `reg`; nested required properties found across the schema include `compatible`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 2 top-level properties and 2 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-safety.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-safety.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-scaling-engine.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-scaling-engine.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-scaling-engine.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Scaling Engine` NXP/Freescale i.MX display block binding. The unit can change the dimension of the input frame by nearest or linear re-sampling with 1/32 sub pixel precision. Internally it consist of two independent blocks for horizontal and vertical scaling. The sequence of both operations is arbitrary. Any frame dimensions between 1 and 16384 pixels in width and height are supported, except that the vertical scaler has a frame width maximum depending of the system's functional limitations. In general all scale factors are supported inside the supported frame dimensions. In range of scale factors 1/16..16 the filtered output colors are LSBit precise (e.g. DC ripple free). +-----------+ | Line | | Buffer | +-----------+ ^ | V |\ +-----------+ ------+ | | | | | +-->| Vertical |---- | ----+ | | Scaler | |... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 2 compatible tokens: `fsl,imx8qxp-dc-hscaler`, `fsl,imx8qxp-dc-vscaler`. Top-level properties are `compatible`, `reg`, `reg-names`. Top-level required properties are `compatible`, `reg`, `reg-names`; nested required properties found across the schema include `compatible`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-scaling-engine.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-scaling-engine.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-signature.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-signature.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-signature.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Signature Unit` NXP/Freescale i.MX display block binding. In order to control the correctness of display output, signature values can be computed for each frame and compared against reference values. In case of a mismatch (signature violation) a HW event can be triggered, for example a SW interrupt. This unit supports signature computation, reference check, evaluation windows, alpha masking and panic modes. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-signature`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`. Top-level required properties are `compatible`, `reg`, `interrupts`, `interrupt-names`; nested required properties found across the schema include `compatible`, `interrupt-names`, `interrupts`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`, `interrupt-names`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 4 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-signature.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-signature.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-store.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-store.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-store.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Store Unit` NXP/Freescale i.MX display block binding. The Store unit is the interface between the internal pixel processing pipeline, which is 30-bit RGB plus 8-bit Alpha, and the AXI bus for destination buffer access. It is used for the destination of Blit Engines. It comprises a set of built-in functions to generate a wide range of buffer formats. Note, that these are exactly inverse to corresponding functions in the Fetch Unit. +------X-------------------------+ | | Store Unit | | V | | +-------+ | | | Gamma | Gamma apply | | +-------+ | | | | | V | | +-------+ | | | Color | RGB to YUV | | +-------+ | | | | | V | | +-------+ | | | Chroma| YUV444 to 422 | | +-------+ | | | | | V | | +-------+ | | | Reduce| Bit width reduction | | | | dithering | | +-------+ | | | | | V | | +-------+ | | | Pack | RG... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-store`. Top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `fsl,lts`. Top-level required properties are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`; nested required properties found across the schema include `compatible`, `interrupt-names`, `interrupts`, `reg`, `reg-names`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`, `interrupt-names`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-store.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-store.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-tcon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-tcon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-tcon.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller Timing Controller` NXP/Freescale i.MX display block binding. The TCon can generate a wide range of customized synchronization signals and does the mapping of the color bits to the output. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc-tcon`. Top-level properties are `compatible`, `reg`, `port`. Top-level required properties are `compatible`, `reg`, `port`; nested required properties found across the schema include `compatible`, `port`, `reg`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-tcon.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc-tcon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc.yaml` is a Linux devicetree YAML schema for the `Freescale i.MX8qxp Display Controller` NXP/Freescale i.MX display block binding. The Freescale i.MX8qxp Display Controller(DC) is comprised of three main components that include a blit engine for 2D graphics accelerations, display controller for display output processing, as well as a command sequencer. Display buffers Source buffers (AXI read master) (AXI read master) | .......... | | | | +---------------------------+------------+------------------+-+-+------+ | Display Controller (DC) | .......... | | | | | | | | | | | | | @@@@@@@@@@@ +----------+------------+------------+ | | | | A | | Command | | V V | | | | | X <-+->| Sequencer | | @@@@@@@@@@@@@@@@@@@@@@@@@@@@ | V V V | I | | (AXI CLK) | | | | | @@@@@@@@@@ | | @@@@@@@@@@@ | | Pixel Engine | | | | | | | | | (AXI CLK) | | | | | | V | @@@@@@@@@@@@@@@@@@@@@@@@@@@@ | | | | A |... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-dc`. Top-level properties are `compatible`, `reg`, `clocks`, `resets`, `reset-names`, `power-domains`, `#address-cells`, `#size-cells`, `ranges`. Top-level required properties are `compatible`, `reg`, `clocks`, `power-domains`, `#address-cells`, `#size-cells`, `ranges`; nested required properties found across the schema include `#address-cells`, `#size-cells`, `clocks`, `compatible`, `power-domains`, `ranges`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: `resets`, `reset-names`; regulators/power: `power-domains`; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Liu Ying <victor.liu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are `^command-sequencer@[0-9a-f]+$`, `^display-engine@[0-9a-f]+$`, `^interrupt-controller@[0-9a-f]+$`, `^pixel-engine@[0-9a-f]+$`, `^pmu@[0-9a-f]+$`; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 9 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/fsl,imx8qxp-dc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/nxp,imx8mq-dcss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/nxp,imx8mq-dcss.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/nxp,imx8mq-dcss.yaml` is a Linux devicetree YAML schema for the `iMX8MQ Display Controller Subsystem (DCSS)` NXP/Freescale i.MX display block binding. The DCSS (display controller sub system) is used to source up to three display buffers, compose them, and drive a display using HDMI 2.0a(with HDCP 2.2) or MIPI-DSI. The DCSS is intended to support up to 4kp60 displays. HDR10 image processing capabilities are included to provide a solution capable of driving next generation high dynamic range displays. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `nxp,imx8mq-dcss`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `assigned-clock-rates`, `port`. Top-level required properties are none declared at the top level; nested required properties found across the schema include none. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `assigned-clock-rates`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`, `interrupt-names`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurentiu Palcu <laurentiu.palcu@nxp.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 10 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/imx/nxp,imx8mq-dcss.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/imx/nxp,imx8mq-dcss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ingenic,ipu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ingenic,ipu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ingenic,ipu.yaml` is a Linux devicetree YAML schema for the `Ingenic SoCs Image Processing Unit (IPU)` display controller binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 2 accepted compatible forms and covers 3 compatible tokens: `ingenic,jz4725b-ipu`, `ingenic,jz4760-ipu`, `ingenic,jz4770-ipu`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `port`. Top-level required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Paul Cercueil <paul@crapouillou.net>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/ingenic,ipu.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ingenic,ipu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ingenic,lcd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ingenic,lcd.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ingenic,lcd.yaml` is a Linux devicetree YAML schema for the `Ingenic SoCs LCD controller` display controller binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 6 compatible tokens: `ingenic,jz4740-lcd`, `ingenic,jz4725b-lcd`, `ingenic,jz4760-lcd`, `ingenic,jz4760b-lcd`, `ingenic,jz4770-lcd`, `ingenic,jz4780-lcd`. Top-level properties are `$nodename`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `port`, `ports`. Top-level required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `port@0`, `reg`. Graph integration is expressed through `port`, `port@0`, `port@8`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Paul Cercueil <paul@crapouillou.net>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Pattern properties are none; top-level composition/conditional keys are `if`, `then`, `else`; the file provides 2 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 8 top-level properties and 10 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/ingenic,lcd.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ingenic,lcd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/intel,keembay-display.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/intel,keembay-display.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/intel,keembay-display.yaml` is a Linux devicetree YAML schema for the `Intel Keem Bay display controller` display controller binding. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `intel,keembay-display`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `port`. Top-level required properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `port`; nested required properties found across the schema include `clock-names`, `clocks`, `compatible`, `interrupts`, `port`, `reg`, `reg-names`. Graph integration is expressed through `port`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`, `clock-names`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Anitha Chrisanthus <anitha.chrisanthus@intel.com>, Edmond J Dea <edmund.j.dea@intel.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 7 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/intel,keembay-display.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/intel,keembay-display.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/intel,keembay-msscam.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/intel,keembay-msscam.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/intel,keembay-msscam.yaml` is a Linux devicetree YAML schema for the `Intel Keem Bay MSSCAM` display controller binding. MSSCAM controls local clocks in the display subsystem namely LCD clocks and MIPI DSI clocks. It also configures the interconnect between LCD and MIPI DSI. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses ordered `items` sequence and covers 2 compatible tokens: `intel,keembay-msscam`, `syscon`. Top-level properties are `compatible`, `reg`, `reg-io-width`. Top-level required properties are `compatible`, `reg`, `reg-io-width`; nested required properties found across the schema include `compatible`, `reg`, `reg-io-width`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Anitha Chrisanthus <anitha.chrisanthus@intel.com>, Edmond J Dea <edmund.j.dea@intel.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 3 top-level properties and 3 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/intel,keembay-msscam.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/intel,keembay-msscam.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds-data-mapping.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds-data-mapping.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds-data-mapping.yaml` is a Linux devicetree YAML schema for the `LVDS Data Mapping` LVDS display binding. LVDS is a physical layer specification defined in ANSI/TIA/EIA-644-A. Multiple incompatible data link layers have been used over time to transmit image data to LVDS devices. This bindings supports devices compatible with the following specifications. [JEIDA] "Digital Interface Standards for Monitor", JEIDA-59-1999, February 1999 (Version 1.0), Japan Electronic Industry Development Association (JEIDA) [LDI] "Open LVDS Display Interface", May 1999 (Version 0.95), National Semiconductor [VESA] "VESA Notebook Panel Standard", October 2007 (Version 1.0), Video Electronics Standards Association (VESA) Device compatible with those specifications have been marketed under the FPD-Link and FlatLink brands. This bindings also supports 30-bit data mapping com... It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses no explicit compatible schema and covers 0 compatible tokens: no explicit compatible values. Top-level properties are `data-mapping`. Top-level required properties are none declared at the top level; nested required properties found across the schema include none. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include `data-mapping`. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>, Thierry Reding <thierry.reding@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 0 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 1 top-level properties and 1 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level extra properties are intentionally allowed. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/lvds-data-mapping.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds-data-mapping.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds.yaml` is a Linux devicetree YAML schema for the `LVDS Display Common Properties` LVDS display binding. This binding extends the data mapping defined in lvds-data-mapping.yaml. It supports reversing the bit order on the formats defined there in order to accommodate for even more specialized data formats, since a variety of data formats and layouts is used to drive LVDS displays. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses no explicit compatible schema and covers 0 compatible tokens: no explicit compatible values. Top-level properties are `data-mirror`. Top-level required properties are none declared at the top level; nested required properties found across the schema include none. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: none; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Laurent Pinchart <laurent.pinchart+renesas@ideasonboard.com>, Thierry Reding <thierry.reding@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `lvds-data-mapping.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 0 example blocks.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 1 top-level properties and 1 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level extra properties are intentionally allowed. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/lvds.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/lvds.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mayqueen,pixpaper.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mayqueen,pixpaper.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mayqueen,pixpaper.yaml` is a Linux devicetree YAML schema for the `Mayqueen Pixpaper e-ink display panel` display panel binding. The Pixpaper is an e-ink display panel controlled via an SPI interface. The panel has a resolution of 122x250 pixels and requires GPIO pins for reset, busy, and data/command control. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses single `const` and covers 1 compatible token: `mayqueen,pixpaper`. Top-level properties are `compatible`, `reg`, `spi-max-frequency`, `reset-gpios`, `busy-gpios`, `dc-gpios`. Top-level required properties are `compatible`, `reg`, `reset-gpios`, `busy-gpios`, `dc-gpios`; nested required properties found across the schema include `busy-gpios`, `compatible`, `dc-gpios`, `reg`, `reset-gpios`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: none; resets: `reset-gpios`; regulators/power: none; IRQ/DMA-related: none.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: LiangCheng Wang <zaq14760@gmail.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/spi/spi-peripheral-props.yaml#`. Pattern properties are none; top-level composition/conditional keys are `allOf`; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 6 top-level properties and 6 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: composed schemas are closed with `unevaluatedProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/mayqueen,pixpaper.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mayqueen,pixpaper.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,aal.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,aal.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,aal.yaml` is a Linux devicetree YAML schema for the `Mediatek display adaptive ambient light processor` MediaTek display pipeline binding. Mediatek display adaptive ambient light processor, namely AAL, is responsible for backlight power saving and sunlight visibility improving. AAL device node must be siblings to the central MMSYS_CONFIG node. For a description of the MMSYS_CONFIG binding, see Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml for details. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 4 accepted compatible forms and covers 12 compatible tokens: `mediatek,mt8173-disp-aal`, `mediatek,mt8183-disp-aal`, `mediatek,mt8195-mdp3-aal`, `mediatek,mt8188-mdp3-aal`, `mediatek,mt2712-disp-aal`, `mediatek,mt6795-disp-aal`, `mediatek,mt8167-disp-aal`, `mediatek,mt8186-disp-aal`, `mediatek,mt8188-disp-aal`, `mediatek,mt8192-disp-aal`, `mediatek,mt8195-disp-aal`, `mediatek,mt8365-disp-aal`. Top-level properties are `compatible`, `reg`, `interrupts`, `power-domains`, `clocks`, `mediatek,gce-client-reg`, `ports`. Top-level required properties are `compatible`, `reg`, `interrupts`, `power-domains`, `clocks`; nested required properties found across the schema include `clocks`, `compatible`, `interrupts`, `port@0`, `port@1`, `power-domains`, `reg`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: `power-domains`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Chun-Kuang Hu <chunkuang.hu@kernel.org>, Philipp Zabel <p.zabel@pengutronix.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle-array`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/mediatek/mediatek,aal.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,aal.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ccorr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ccorr.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ccorr.yaml` is a Linux devicetree YAML schema for the `Mediatek display color correction` MediaTek display pipeline binding. Mediatek display color correction, namely CCORR, reproduces correct color on panels with different color gamut. CCORR device node must be siblings to the central MMSYS_CONFIG node. For a description of the MMSYS_CONFIG binding, see Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml for details. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 3 accepted compatible forms and covers 7 compatible tokens: `mediatek,mt8183-disp-ccorr`, `mediatek,mt8192-disp-ccorr`, `mediatek,mt8167-disp-ccorr`, `mediatek,mt8365-disp-ccorr`, `mediatek,mt8186-disp-ccorr`, `mediatek,mt8188-disp-ccorr`, `mediatek,mt8195-disp-ccorr`. Top-level properties are `compatible`, `reg`, `interrupts`, `power-domains`, `clocks`, `mediatek,gce-client-reg`, `ports`. Top-level required properties are `compatible`, `reg`, `interrupts`, `power-domains`, `clocks`; nested required properties found across the schema include `clocks`, `compatible`, `interrupts`, `port@0`, `port@1`, `power-domains`, `reg`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: `power-domains`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Chun-Kuang Hu <chunkuang.hu@kernel.org>, Philipp Zabel <p.zabel@pengutronix.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle-array`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/mediatek/mediatek,ccorr.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ccorr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,cec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,cec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,cec.yaml` is a Linux devicetree YAML schema for the `Mediatek HDMI CEC Controller` MediaTek display pipeline binding. The HDMI CEC controller handles hotplug detection and CEC communication. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `enum` list and covers 3 compatible tokens: `mediatek,mt7623-cec`, `mediatek,mt8167-cec`, `mediatek,mt8173-cec`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Top-level required properties are `compatible`, `reg`, `interrupts`, `clocks`; nested required properties found across the schema include `clocks`, `compatible`, `interrupts`, `reg`. Graph integration is expressed through no explicit graph ports; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: none; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: CK Hu <ck.hu@mediatek.com>, Jitao shi <jitao.shi@mediatek.com>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are no external `$ref` beyond the core meta-schema. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 4 top-level properties and 4 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/mediatek/mediatek,cec.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,cec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,color.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,color.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,color.yaml` is a Linux devicetree YAML schema for the `Mediatek display color processor` MediaTek display pipeline binding. Mediatek display color processor, namely COLOR, provides hue, luma and saturation adjustments to get better picture quality and to have one panel resemble the other in their output characteristics. COLOR device node must be siblings to the central MMSYS_CONFIG node. For a description of the MMSYS_CONFIG binding, see Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml for details. It is not driver code; it is the ABI and validation contract that DTS files must satisfy before the corresponding DRM, fbdev, MIPI DSI, connector, panel, or platform-display driver can bind predictably.

## Important APIs, Types, and Functions
The public schema API is the set of devicetree properties and child-node shapes it accepts. `compatible` uses `oneOf` with 4 accepted compatible forms and covers 14 compatible tokens: `mediatek,mt2701-disp-color`, `mediatek,mt8167-disp-color`, `mediatek,mt8173-disp-color`, `mediatek,mt8195-mdp3-color`, `mediatek,mt8188-mdp3-color`, `mediatek,mt7623-disp-color`, `mediatek,mt2712-disp-color`, `mediatek,mt6795-disp-color`, `mediatek,mt8183-disp-color`, `mediatek,mt8186-disp-color`, `mediatek,mt8188-disp-color`, `mediatek,mt8192-disp-color`, `mediatek,mt8195-disp-color`, `mediatek,mt8365-disp-color`. Top-level properties are `compatible`, `reg`, `interrupts`, `power-domains`, `clocks`, `mediatek,gce-client-reg`, `ports`. Top-level required properties are `compatible`, `reg`, `interrupts`, `power-domains`, `clocks`; nested required properties found across the schema include `clocks`, `compatible`, `interrupts`, `port@0`, `port@1`, `power-domains`, `reg`. Graph integration is expressed through `port@0`, `port@1`, `ports`; endpoint-specific constraints include standard graph endpoint fields only. Resource hooks include clocks: `clocks`; resets: none; regulators/power: `power-domains`; IRQ/DMA-related: `interrupts`.

## Control Flow, State, and Persistence
Control flow is declarative dt-schema evaluation. `dt_binding_check` parses the YAML, applies referenced common schemas, selects conditional branches such as SoC-specific compatible fallback rules, validates required properties and graph endpoint topology, and rejects or permits extra properties according to the schema flags. At runtime the kernel drivers consume the resulting flattened devicetree node, but this file itself keeps no mutable state and performs no persistence. Its persistent behavior is the stable DTS ABI for compatible strings, register resources, clocks, resets, GPIOs, supplies, interrupts, ports, and child nodes.

## Dependencies and Integration Points
Maintainers: Chun-Kuang Hu <chunkuang.hu@kernel.org>, Philipp Zabel <p.zabel@pengutronix.de>. It integrates with Linux devicetree documentation, `dt-doc-validate`, `dt_binding_check`, `dtbs_check`, and DTS users under the same source tree. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle-array`. Pattern properties are none; top-level composition/conditional keys are none; the file provides 1 example block.

## Risks
Risks center on ABI compatibility: changing compatible ordering, required properties, port numbering, lane definitions, or resource names can break existing DTS files or driver probing. This schema has 7 top-level properties and 9 distinct property names when nested graph/child schemas are included, so broad edits can have wider validation impact than they first appear. The strictness profile is: top-level unknown properties are rejected by `additionalProperties: false`. Any conditional compatible table should be checked against all in-tree DTS users, because a schema-only change can reject valid boards even when no driver code changed.

## Test Signals
Primary signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/mediatek/mediatek,color.yaml` and `make dtbs_check` for boards that instantiate the binding. Example validation should exercise the included examples, while integration coverage comes from in-tree DTS nodes using the listed compatible strings and graph endpoints. For bridge and connector bindings, also inspect DRM bridge/panel graph links for correct `remote-endpoint`, port index, lane, supply, reset, HPD, and interrupt wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,color.yaml -->
