# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/adi,adv7533.yaml

## Purpose
Analog Devices ADV7533/35 HDMI Encoders is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `adi,adv7533.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The ADV7533 and ADV7535 are HDMI audio and video transmitters compatible with HDMI 1.4 and DVI 1.0. They support color space conversion, S/PDIF, CEC and HDCP. The transmitter input is MIPI DSI.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/adi,adv7533.yaml#`, top-level `compatible` values `adi,adv7533`, `adi,adv7535`, required properties `compatible`, `reg`, `ports`, `adi,dsi-lanes`, `avdd-supply`, `dvdd-supply`, `pvdd-supply`, `a2vdd-supply`, `v3p3-supply`, and top-level properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `pd-gpios`, `avdd-supply`, `dvdd-supply`, `pvdd-supply`, `a2vdd-supply`, `v3p3-supply`, `v1p2-supply`, `adi,disable-timing-generator`, `adi,dsi-lanes`, `#sound-dai-cells`, `ports`.
Key property contracts include: `compatible` (enum `adi,adv7533`, `adi,adv7535`); `reg` (maxItems=4; minItems=1; I2C slave addresses. The ADV7533/35 internal registers are split into four pages exposed through different I2C addresses, creating four register maps. Each map has it own I2C address and acts as a standard slave device on the I2C bus. The main address is mandatory, others are optional and revert to defaults if not s...); `clocks` (maxItems=1; Reference to the CEC clock.); `clock-names` (const `cec`); `interrupts` (maxItems=1); `adi,disable-timing-generator` (Disables the internal timing generator. The chip will rely on the sync signals in the DSI data lanes, rather than generating its own timings for HDMI output.); `adi,dsi-lanes` (enum `2`, `3`, `4`; ref `/schemas/types.yaml#/definitions/uint32`; Number of DSI data lanes connected to the DSI host.); `#sound-dai-cells` (const `0`); `ports` (ref `/schemas/graph.yaml#/properties/ports`; The ADV7533/35 has two video ports and one audio port.).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `adi,adv7533`, `adi,adv7535`; provider bindings for `clocks`, `clock-names`, `interrupts`, `ports`.
Referenced shared schemas include `/schemas/sound/dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/adi,adv7533.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (188 lines). Maintainers listed by the binding: `Laurent Pinchart <laurent.pinchart@ideasonboard.com>`.
