# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx93-mipi-dsi.yaml

## Purpose
Freescale i.MX93 specific extensions to Synopsys Designware MIPI DSI is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx93-mipi-dsi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. There is a Synopsys Designware MIPI DSI Host Controller and a Synopsys Designware MIPI DPHY embedded in Freescale i.MX93 SoC. Some configurations and extensions to them are controlled by i.MX93 media blk-ctrl.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx93-mipi-dsi.yaml#`, top-level `compatible` values `fsl,imx93-mipi-dsi`, required properties `compatible`, `interrupts`, `fsl,media-blk-ctrl`, `power-domains`, and top-level properties `compatible`, `clocks`, `clock-names`, `interrupts`, `fsl,media-blk-ctrl`, `power-domains`.
Key property contracts include: `compatible` (const `fsl,imx93-mipi-dsi`); `clocks` (declared by schema); `clock-names` (declared by schema); `interrupts` (maxItems=1); `fsl,media-blk-ctrl` (ref `/schemas/types.yaml#/definitions/phandle`; i.MX93 media blk-ctrl, as a syscon, controls pixel component bit map configurations from LCDIF display controller to the MIPI DSI host controller and MIPI DPHY PLL related configurations through PLL SoC interface.); `power-domains` (maxItems=1).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx93-mipi-dsi`; provider bindings for `clocks`, `clock-names`, `interrupts`, `power-domains`.
Referenced shared schemas include `snps,dw-mipi-dsi.yaml#`, `/schemas/types.yaml#/definitions/phandle`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx93-mipi-dsi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (115 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
