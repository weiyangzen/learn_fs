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
