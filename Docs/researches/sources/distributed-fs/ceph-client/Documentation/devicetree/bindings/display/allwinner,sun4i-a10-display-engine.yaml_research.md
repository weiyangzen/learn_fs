# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-engine.yaml

## Purpose
Allwinner A10 Display Engine Pipeline is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun4i-a10-display-engine.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The display engine pipeline (and its entry point, since it can be either directly the backend or the frontend) is represented as an extra node. The Allwinner A10 Display pipeline is composed of several components that are going to be documented below: For all connections between components up to the TCONs in the dis...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun4i-a10-display-engine.yaml#`, top-level `compatible` values `allwinner,sun4i-a10-display-engine`, `allwinner,sun5i-a10s-display-engine`, `allwinner,sun5i-a13-display-engine`, `allwinner,sun6i-a31-display-engine`, `allwinner,sun6i-a31s-display-engine`, `allwinner,sun7i-a20-display-engine`, `allwinner,sun8i-a23-display-engine`, `allwinner,sun8i-a33-display-engine`, `allwinner,sun8i-a83t-display-engine`, `allwinner,sun8i-h3-display-engine`, `allwinner,sun8i-r40-display-engine`, `allwinner,sun8i-v3s-display-engine`, `allwinner,sun9i-a80-display-engine`, `allwinner,sun20i-d1-display-engine`, and 2 more, required properties `compatible`, `allwinner,pipelines`, and top-level properties `compatible`, `allwinner,pipelines`.
Key property contracts include: `compatible` (enum `allwinner,sun4i-a10-display-engine`, `allwinner,sun5i-a10s-display-engine`, `allwinner,sun5i-a13-display-engine`, `allwinner,sun6i-a31-display-engine`, `allwinner,sun6i-a31s-display-engine`, `allwinner,sun7i-a20-display-engine`, `allwinner,sun8i-a23-display-engine`, `allwinner,sun8i-a33-display-engine`, and 8 more); `allwinner,pipelines` (maxItems=2; minItems=1; ref `/schemas/types.yaml#/definitions/phandle-array`; Available display engine frontends (DE 1.0) or mixers (DE 2.0/3.0) available.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun4i-a10-display-engine`, `allwinner,sun5i-a10s-display-engine`, `allwinner,sun5i-a13-display-engine`, `allwinner,sun6i-a31-display-engine`, and 12 more.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle-array`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-engine.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (117 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
