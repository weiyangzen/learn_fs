# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,am62l-dthev2.yaml

## Purpose
K3 SoC DTHE V2 crypto module is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ti,am62l-dthev2.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for K3 SoC DTHE V2 crypto module.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/ti,am62l-dthev2.yaml#`, top-level `compatible` values `ti,am62l-dthev2`, required properties `compatible`, `reg`, `dmas`, `dma-names`, and top-level properties `compatible`, `reg`, `dmas`, `dma-names`.
Key property contracts include: `compatible` (enum `ti,am62l-dthev2`); `reg` (maxItems=1); `dmas` (declared by schema); `dma-names` (declared by schema).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `ti,am62l-dthev2`; provider bindings for `dmas`, `dma-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/ti,am62l-dthev2.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (50 lines). Maintainers listed by the binding: `T Pratham <t-pratham@ti.com>`.
