# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel,lcdc.yaml

## Purpose
Microchip's LCDC Framebuffer is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `atmel,lcdc.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The LCDC works with a framebuffer, which is a section of memory that contains a complete frame of data representing pixel values for the display. The LCDC reads the pixel data from the framebuffer and sends it to the LCD panel to render the image.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/atmel,lcdc.yaml#`, top-level `compatible` values `atmel,at91sam9261-lcdc`, `atmel,at91sam9263-lcdc`, `atmel,at91sam9g10-lcdc`, `atmel,at91sam9g45-lcdc`, `atmel,at91sam9g45es-lcdc`, `atmel,at91sam9rl-lcdc`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `display`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `display`.
Key property contracts include: `compatible` (enum `atmel,at91sam9261-lcdc`, `atmel,at91sam9263-lcdc`, `atmel,at91sam9g10-lcdc`, `atmel,at91sam9g45-lcdc`, `atmel,at91sam9g45es-lcdc`, `atmel,at91sam9rl-lcdc`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (maxItems=2); `clock-names` (declared by schema).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `atmel,at91sam9261-lcdc`, `atmel,at91sam9263-lcdc`, `atmel,at91sam9g10-lcdc`, `atmel,at91sam9g45-lcdc`, and 2 more; provider bindings for `clocks`, `clock-names`, `interrupts`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/atmel,lcdc.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (70 lines). Maintainers listed by the binding: `Nicolas Ferre <nicolas.ferre@microchip.com>`, `Dharma Balasubiramani <dharma.b@microchip.com>`.
