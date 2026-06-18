# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/adi,adv7511.yaml

## Purpose
Analog Devices ADV7511/11W/13 HDMI Encoders is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `adi,adv7511.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The ADV7511, ADV7511W and ADV7513 are HDMI audio and video transmitters compatible with HDMI 1.4 and DVI 1.0. They support color space conversion, S/PDIF, CEC and HDCP. The transmitter input is parallel RGB or YUV data.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/adi,adv7511.yaml#`, top-level `compatible` values `adi,adv7511`, `adi,adv7511w`, `adi,adv7513`, required properties `compatible`, `reg`, `ports`, `adi,input-depth`, `adi,input-colorspace`, `adi,input-clock`, `avdd-supply`, `dvdd-supply`, `pvdd-supply`, `dvdd-3v-supply`, `bgvdd-supply`, and top-level properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `pd-gpios`, `avdd-supply`, `dvdd-supply`, `pvdd-supply`, `dvdd-3v-supply`, `bgvdd-supply`, `adi,input-depth`, `adi,input-colorspace`, `adi,input-clock`, `adi,clock-delay`, `adi,embedded-sync`, `adi,input-style`, and 2 more.
Key property contracts include: `compatible` (enum `adi,adv7511`, `adi,adv7511w`, `adi,adv7513`); `reg` (maxItems=4; minItems=1; I2C slave addresses. The ADV7511/11W/13 internal registers are split into four pages exposed through different I2C addresses, creating four register maps. Each map has it own I2C address and acts as a standard slave device on the I2C bus. The main address is mandatory, others are optional and revert to defaults if n...); `clocks` (maxItems=1; Reference to the CEC clock.); `clock-names` (const `cec`); `interrupts` (maxItems=1); `adi,input-depth` (enum `8`, `10`, `12`; ref `/schemas/types.yaml#/definitions/uint32`; Number of bits per color component at the input.); `adi,input-colorspace` (enum `rgb`, `yuv422`, `yuv444`; Input color space.); `adi,input-clock` (enum `1x`, `2x`, `dd`; Input clock type. "1x": one clock cycle per pixel "2x": two clock cycles per pixel "dd": one clock cycle per pixel, data driven on both edges); `adi,clock-delay` (ref `/schemas/types.yaml#/definitions/uint32`; Video data clock delay relative to the pixel clock, in ps (-1200ps .. 1600 ps).); `adi,embedded-sync` (If defined, the input uses synchronization signals embedded in the data stream (similar to BT.656).); `adi,input-style` (enum `1`, `2`, `3`; ref `/schemas/types.yaml#/definitions/uint32`; Input components arrangement variant as listed in the input format tables in the datasheet.); `adi,input-justification` (enum `left`, `evenly`, `right`; Input bit justification.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `adi,adv7511`, `adi,adv7511w`, `adi,adv7513`; provider bindings for `clocks`, `clock-names`, `interrupts`, `ports`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/adi,adv7511.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (236 lines). Maintainers listed by the binding: `Laurent Pinchart <laurent.pinchart@ideasonboard.com>`.
