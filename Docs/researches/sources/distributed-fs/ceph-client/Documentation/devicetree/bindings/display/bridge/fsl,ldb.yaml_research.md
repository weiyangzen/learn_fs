# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,ldb.yaml

## Purpose
Freescale i.MX8MP DPI to LVDS bridge chip is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,ldb.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The i.MX8MP mediamix contains two registers which are responsible for configuring the on-SoC DPI-to-LVDS serializer. This describes those registers as bridge within the DT.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,ldb.yaml#`, top-level `compatible` values `fsl,imx6sx-ldb`, `fsl,imx8mp-ldb`, `fsl,imx93-ldb`, required properties `compatible`, `clocks`, `ports`, `reg`, and top-level properties `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `nxp,enable-termination-resistor`, `ports`.
Key property contracts include: `compatible` (enum `fsl,imx6sx-ldb`, `fsl,imx8mp-ldb`, `fsl,imx93-ldb`); `clocks` (maxItems=1); `clock-names` (const `ldb`); `reg` (maxItems=2); `nxp,enable-termination-resistor` (Indicates that the built-in 100 Ohm termination resistor on the LVDS output is enabled. This property is optional and controlled via the HS_EN bit in the LVDS_CTRL register. Enabling it can improve signal quality and prevent visual artifacts on some boards, but increases power consumption.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx6sx-ldb`, `fsl,imx8mp-ldb`, `fsl,imx93-ldb`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,ldb.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (150 lines). Maintainers listed by the binding: `Marek Vasut <marex@denx.de>`.
