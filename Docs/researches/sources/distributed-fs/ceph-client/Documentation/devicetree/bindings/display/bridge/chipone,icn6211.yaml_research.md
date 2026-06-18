# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/chipone,icn6211.yaml

## Purpose
Chipone ICN6211 MIPI-DSI to RGB Converter bridge is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `chipone,icn6211.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. ICN6211 is MIPI-DSI to RGB Converter bridge from chipone. It has a flexible configuration of MIPI DSI signal input and produce RGB565, RGB666, RGB888 output format.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/chipone,icn6211.yaml#`, top-level `compatible` values `chipone,icn6211`, required properties `compatible`, `reg`, `enable-gpios`, `ports`, and top-level properties `compatible`, `reg`, `clock-names`, `clocks`, `enable-gpios`, `vdd1-supply`, `vdd2-supply`, `vdd3-supply`, `ports`.
Key property contracts include: `compatible` (enum `chipone,icn6211`); `reg` (maxItems=1; virtual channel number of a DSI peripheral); `clock-names` (const `refclk`); `clocks` (maxItems=1; Optional external clock connected to REF_CLK input. The clock rate must be in 10..154 MHz range.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `chipone,icn6211`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/chipone,icn6211.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (123 lines). Maintainers listed by the binding: `Jagan Teki <jagan@amarulasolutions.com>`.
