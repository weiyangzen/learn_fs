# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-dw-hdmi.yaml

## Purpose
Amlogic specific extensions to the Synopsys Designware HDMI Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `amlogic,meson-dw-hdmi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Amlogic Meson Synopsys Designware Integration is composed of - A Synopsys DesignWare HDMI Controller IP - A TOP control block controlling the Clocks and PHY - A custom HDMI PHY in order to convert video to TMDS signal ___________________________________ | HDMI TOP |<= HPD |___________________________________| |...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/amlogic,meson-dw-hdmi.yaml#`, top-level `compatible` values `amlogic,meson-gxbb-dw-hdmi`, `amlogic,meson-gxl-dw-hdmi`, `amlogic,meson-gxm-dw-hdmi`, `amlogic,meson-gx-dw-hdmi`, `amlogic,meson-g12a-dw-hdmi`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `port@0`, `port@1`, `#address-cells`, `#size-cells`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `hdmi-supply`, `port@0`, `port@1`, `#address-cells`, `#size-cells`, `#sound-dai-cells`, `sound-name-prefix`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (minItems=3); `clock-names` (declared by schema); `power-domains` (maxItems=1; phandle to the associated power domain); `resets` (minItems=3); `reset-names` (declared by schema); `#address-cells` (const `1`); `#size-cells` (const `0`); `#sound-dai-cells` (const `0`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `amlogic,meson-gxbb-dw-hdmi`, `amlogic,meson-gxl-dw-hdmi`, `amlogic,meson-gxm-dw-hdmi`, `amlogic,meson-gx-dw-hdmi`, and 1 more; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `power-domains`.
Referenced shared schemas include `/schemas/sound/dai-common.yaml#`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/amlogic,meson-dw-hdmi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (157 lines). Maintainers listed by the binding: `Neil Armstrong <neil.armstrong@linaro.org>`.
