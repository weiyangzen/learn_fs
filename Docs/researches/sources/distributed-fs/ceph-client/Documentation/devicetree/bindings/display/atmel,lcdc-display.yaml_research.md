# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel,lcdc-display.yaml

## Purpose
Microchip's LCDC Display is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `atmel,lcdc-display.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The LCD Controller (LCDC) consists of logic for transferring LCD image data from an external display buffer to a TFT LCD panel. The LCDC has one display input buffer per layer that fetches pixels through the single bus host interface and a look-up table to allow palletized display configurations. The LCDC is program...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/atmel,lcdc-display.yaml#`, top-level `compatible` values none declared, required properties `atmel,dmacon`, `atmel,lcdcon2`, `atmel,guard-time`, `bits-per-pixel`, and top-level properties `atmel,dmacon`, `atmel,lcdcon2`, `atmel,guard-time`, `bits-per-pixel`, `atmel,lcdcon-backlight`, `atmel,lcdcon-backlight-inverted`, `atmel,lcd-wiring-mode`, `atmel,power-control-gpio`, `display-timings`.
Key property contracts include: `atmel,dmacon` (ref `/schemas/types.yaml#/definitions/uint32`; dma controller configuration); `atmel,lcdcon2` (ref `/schemas/types.yaml#/definitions/uint32`; lcd controller configuration); `atmel,guard-time` (ref `/schemas/types.yaml#/definitions/uint32`; lcd guard time (Delay in frame periods)); `atmel,lcdcon-backlight` (ref `/schemas/types.yaml#/definitions/flag`; enable backlight); `atmel,lcdcon-backlight-inverted` (ref `/schemas/types.yaml#/definitions/flag`; invert backlight PWM polarity); `atmel,lcd-wiring-mode` (enum `RGB`, `BRG`; ref `/schemas/types.yaml#/definitions/string`; lcd wiring mode "RGB" or "BRG"); `atmel,power-control-gpio` (maxItems=1; gpio to power on or off the LCD (as many as needed)).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `panel/display-timings.yaml#`.

## Risks
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/atmel,lcdc-display.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (103 lines). Maintainers listed by the binding: `Nicolas Ferre <nicolas.ferre@microchip.com>`, `Dharma Balasubiramani <dharma.b@microchip.com>`.
