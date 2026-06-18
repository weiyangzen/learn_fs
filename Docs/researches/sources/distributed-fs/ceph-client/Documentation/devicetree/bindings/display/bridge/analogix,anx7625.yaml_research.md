# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,anx7625.yaml

## Purpose
Analogix ANX7625 SlimPort (4K Mobile HD Transmitter) is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `analogix,anx7625.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The ANX7625 is an ultra-low power 4K Mobile HD Transmitter designed for portable devices.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/analogix,anx7625.yaml#`, top-level `compatible` values `analogix,anx7625`, required properties `compatible`, `reg`, `vdd10-supply`, `vdd18-supply`, `vdd33-supply`, `ports`, and top-level properties `compatible`, `reg`, `interrupts`, `enable-gpios`, `reset-gpios`, `vdd10-supply`, `vdd18-supply`, `vdd33-supply`, `analogix,lane0-swing`, `analogix,lane1-swing`, `analogix,audio-enable`, `aux-bus`, `connector`, `ports`.
Key property contracts include: `compatible` (const `analogix,anx7625`); `reg` (maxItems=1); `interrupts` (maxItems=1; used for interrupt pin B8.); `analogix,lane0-swing` (maxItems=20; minItems=1; ref `/schemas/types.yaml#/definitions/uint8-array`; an array of swing register setting for DP tx lane0 PHY. Registers 0~9 are Swing0_Pre0, Swing1_Pre0, Swing2_Pre0, Swing3_Pre0, Swing0_Pre1, Swing1_Pre1, Swing2_Pre1, Swing0_Pre2, Swing1_Pre2, Swing0_Pre3, they are for [Boost control] and [Swing control] setting. Registers 0~9, bit 3:0 is [Boost control], these bits c...); `analogix,lane1-swing` (maxItems=20; minItems=1; ref `/schemas/types.yaml#/definitions/uint8-array`; an array of swing register setting for DP tx lane1 PHY. DP TX lane1 swing register setting same with lane0 swing, please refer lane0-swing property description.); `analogix,audio-enable` (let the driver enable audio HDMI codec function or not.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `analogix,anx7625`; provider bindings for `interrupts`, `ports`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/display/dp-aux-bus.yaml#`, `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/analogix,anx7625.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 2 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (283 lines). Maintainers listed by the binding: `Xin Ji <xji@analogixsemi.com>`.
