# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it6263.yaml

## Purpose
ITE IT6263 LVDS to HDMI converter is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ite,it6263.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The IT6263 is a high-performance single-chip De-SSC(De-Spread Spectrum) LVDS to HDMI converter. Combined with LVDS receiver and HDMI 1.4a transmitter, the IT6263 supports LVDS input and HDMI 1.4 output by conversion function. The built-in LVDS receiver can support single-link and dual-link LVDS inputs, and the built...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/ite,it6263.yaml#`, top-level `compatible` values `ite,it6263`, required properties `compatible`, `reg`, `data-mapping`, `ivdd-supply`, `ovdd-supply`, `txavcc18-supply`, `txavcc33-supply`, `pvcc1-supply`, `pvcc2-supply`, `avcc-supply`, `anvdd-supply`, `apvdd-supply`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `data-mapping`, `reset-gpios`, `ivdd-supply`, `ovdd-supply`, `txavcc18-supply`, `txavcc33-supply`, `pvcc1-supply`, `pvcc2-supply`, `avcc-supply`, `anvdd-supply`, `apvdd-supply`, `#sound-dai-cells`, `ite,i2s-audio-fifo-sources`, `ite,rl-channel-swap-audio-sources`, and 1 more.
Key property contracts include: `compatible` (const `ite,it6263`); `reg` (maxItems=1); `clocks` (maxItems=1; audio master clock); `clock-names` (const `mclk`); `#sound-dai-cells` (const `0`); `ite,i2s-audio-fifo-sources` (maxItems=4; minItems=1; ref `/schemas/types.yaml#/definitions/uint32-array`; Each array element indicates the pin number of an I2S serial data input line which is connected to an audio FIFO, from audio FIFO0 to FIFO3.); `ite,rl-channel-swap-audio-sources` (maxItems=4; minItems=1; ref `/schemas/types.yaml#/definitions/uint32-array`; Each array element indicates an audio source whose right channel and left channel are swapped by this converter. For I2S, the element is the pin number of an I2S serial data input line. For S/PDIF, the element is always 0.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `ite,it6263`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `/schemas/display/lvds-dual-ports.yaml#`, `/schemas/sound/dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ite,it6263.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 2 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (251 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
