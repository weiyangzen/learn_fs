# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,pl11x.yaml

## Purpose
Arm PrimeCell Color LCD Controller PL110/PL111 is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `arm,pl11x.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Arm Primcell PL010/PL111 is an LCD controller IP, than scans out a framebuffer region in system memory, and creates timed signals for a variety of LCD panels.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/arm,pl11x.yaml#`, top-level `compatible` values `arm,pl110`, `arm,pl111`, `arm,primecell`, required properties `compatible`, `reg`, `clock-names`, `clocks`, `port`, and top-level properties `compatible`, `reg`, `interrupt-names`, `interrupts`, `clock-names`, `clocks`, `memory-region`, `max-memory-bandwidth`, `resets`, `port`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupt-names` (declared by schema); `interrupts` (maxItems=4; minItems=1); `clock-names` (declared by schema); `clocks` (declared by schema); `resets` (maxItems=1); `port` (ref `/schemas/graph.yaml#/$defs/port-base`; Output endpoint of the controller, connecting the LCD panel signals.).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `arm,pl110`, `arm,pl111`, `arm,primecell`; provider bindings for `clocks`, `clock-names`, `resets`, `interrupts`, `interrupt-names`, `port`, `memory-region`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/types.yaml#/definitions/uint32-array`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/arm,pl11x.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (173 lines). Maintainers listed by the binding: `Liviu Dudau <Liviu.Dudau@arm.com>`, `Andre Przywara <andre.przywara@arm.com>`.
