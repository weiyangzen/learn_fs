# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-tcon.yaml

## Purpose
Allwinner A10 Timings Controller (TCON) is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun4i-a10-tcon.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The TCON acts as a timing controller for RGB, LVDS and TV interfaces.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun4i-a10-tcon.yaml#`, top-level `compatible` values `allwinner,sun4i-a10-tcon`, `allwinner,sun5i-a13-tcon`, `allwinner,sun6i-a31-tcon`, `allwinner,sun6i-a31s-tcon`, `allwinner,sun7i-a20-tcon`, `allwinner,sun8i-a23-tcon`, `allwinner,sun8i-a33-tcon`, `allwinner,sun8i-a83t-tcon-lcd`, `allwinner,sun8i-a83t-tcon-tv`, `allwinner,sun8i-r40-tcon-tv`, `allwinner,sun8i-v3s-tcon`, `allwinner,sun9i-a80-tcon-lcd`, `allwinner,sun9i-a80-tcon-tv`, `allwinner,sun20i-d1-tcon-lcd`, and 7 more, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `ports`, and top-level properties `#clock-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `clock-output-names`, `dmas`, `resets`, `reset-names`, `ports`.
Key property contracts include: `#clock-cells` (const `0`); `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (maxItems=4; minItems=1); `clock-names` (maxItems=4; minItems=1); `dmas` (maxItems=1); `resets` (declared by schema); `reset-names` (declared by schema); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 10 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun4i-a10-tcon`, `allwinner,sun5i-a13-tcon`, `allwinner,sun6i-a31-tcon`, `allwinner,sun6i-a31s-tcon`, and 17 more; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `dmas`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/types.yaml#/definitions/uint32`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun4i-a10-tcon.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 5 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (677 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
