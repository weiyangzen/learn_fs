# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-combiner.yaml

## Purpose
Freescale i.MX8qm/qxp Pixel Combiner is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx8qxp-pixel-combiner.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Freescale i.MX8qm/qxp Pixel Combiner takes two output streams from a single display controller and manipulates the two streams to support a number of modes(bypass, pixel combine, YUV444 to YUV422, split_RGB) configured as either one screen, two screens, or virtual screens. The pixel combiner is also responsible...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx8qxp-pixel-combiner.yaml#`, top-level `compatible` values `fsl,imx8qm-pixel-combiner`, `fsl,imx8qxp-pixel-combiner`, required properties `compatible`, `#address-cells`, `#size-cells`, `reg`, `clocks`, `clock-names`, `power-domains`, and top-level properties `compatible`, `#address-cells`, `#size-cells`, `reg`, `clocks`, `clock-names`, `power-domains`.
Key property contracts include: `compatible` (enum `fsl,imx8qm-pixel-combiner`, `fsl,imx8qxp-pixel-combiner`); `#address-cells` (const `1`); `#size-cells` (const `0`); `reg` (maxItems=1); `clocks` (maxItems=1); `clock-names` (const `apb`); `power-domains` (maxItems=1).
The schema also defines pattern properties `^channel@[0-1]$`, which describe child nodes or reusable node fragments.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx8qm-pixel-combiner`, `fsl,imx8qxp-pixel-combiner`; provider bindings for `clocks`, `clock-names`, `power-domains`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-combiner.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (144 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
