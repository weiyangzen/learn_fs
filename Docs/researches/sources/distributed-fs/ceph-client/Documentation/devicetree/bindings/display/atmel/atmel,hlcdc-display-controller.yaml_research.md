# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel/atmel,hlcdc-display-controller.yaml

## Purpose
Atmel's High LCD Controller (HLCDC) is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `atmel,hlcdc-display-controller.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The LCD Controller (LCDC) consists of logic for transferring LCD image data from an external display buffer to a TFT LCD panel. The LCDC has one display input buffer per layer that fetches pixels through the single bus host interface and a look-up table to allow palletized display configurations.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/atmel/atmel,hlcdc-display-controller.yaml#`, top-level `compatible` values `atmel,hlcdc-display-controller`, required properties `#address-cells`, `#size-cells`, `compatible`, `port@0`, and top-level properties `compatible`, `#address-cells`, `#size-cells`, `port@0`.
Key property contracts include: `compatible` (const `atmel,hlcdc-display-controller`); `#address-cells` (const `1`); `#size-cells` (const `0`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `atmel,hlcdc-display-controller`.
Referenced shared schemas include `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/atmel/atmel,hlcdc-display-controller.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- add or update example nodes when changing required resources so validation covers the intended binding shape

## Source Notes
The source was read in full for this research pass (63 lines). Maintainers listed by the binding: `Nicolas Ferre <nicolas.ferre@microchip.com>`, `Alexandre Belloni <alexandre.belloni@bootlin.com>`, `Claudiu Beznea <claudiu.beznea@tuxon.dev>`.
