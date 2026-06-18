# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pxl2dpi.yaml

## Purpose
Freescale i.MX8qxp Pixel Link to Display Pixel Interface is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx8qxp-pxl2dpi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Freescale i.MX8qxp Pixel Link to Display Pixel Interface(PXL2DPI) interfaces the pixel link 36-bit data output and the DSI controller’s MIPI-DPI 24-bit data input, and inputs of LVDS Display Bridge(LDB) module used in LVDS mode, to remap the pixel color codings between those modules. This module is purely combin...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx8qxp-pxl2dpi.yaml#`, top-level `compatible` values `fsl,imx8qxp-pxl2dpi`, required properties `compatible`, `fsl,sc-resource`, `power-domains`, `ports`, and top-level properties `compatible`, `fsl,sc-resource`, `power-domains`, `fsl,companion-pxl2dpi`, `ports`.
Key property contracts include: `compatible` (const `fsl,imx8qxp-pxl2dpi`); `fsl,sc-resource` (ref `/schemas/types.yaml#/definitions/uint32`; The SCU resource ID associated with this PXL2DPI instance.); `power-domains` (maxItems=1); `fsl,companion-pxl2dpi` (ref `/schemas/types.yaml#/definitions/phandle`; A phandle which points to companion PXL2DPI which is used by downstream LVDS Display Bridge(LDB) in split mode.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx8qxp-pxl2dpi`; provider bindings for `power-domains`, `ports`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pxl2dpi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (108 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
