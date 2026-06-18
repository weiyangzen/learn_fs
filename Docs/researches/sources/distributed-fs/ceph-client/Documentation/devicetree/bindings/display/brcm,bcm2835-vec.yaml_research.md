# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-vec.yaml

## Purpose
Broadcom VC4 (VideoCore4) VEC is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-vec.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom VC4 (VideoCore4) VEC.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-vec.yaml#`, top-level `compatible` values `brcm,bcm2711-vec`, `brcm,bcm2835-vec`, required properties `compatible`, `reg`, `clocks`, `interrupts`, and top-level properties `compatible`, `reg`, `clocks`, `interrupts`, `power-domains`.
Key property contracts include: `compatible` (enum `brcm,bcm2711-vec`, `brcm,bcm2835-vec`); `reg` (maxItems=1); `clocks` (maxItems=1); `interrupts` (maxItems=1); `power-domains` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2711-vec`, `brcm,bcm2835-vec`; provider bindings for `clocks`, `interrupts`, `power-domains`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-vec.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (49 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
