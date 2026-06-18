# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/rockchip,rk3288-crypto.yaml

## Purpose
Rockchip Electronics Security Accelerator is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `rockchip,rk3288-crypto.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Rockchip Electronics Security Accelerator.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/rockchip,rk3288-crypto.yaml#`, top-level `compatible` values `rockchip,rk3288-crypto`, `rockchip,rk3328-crypto`, `rockchip,rk3399-crypto`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`.
Key property contracts include: `compatible` (enum `rockchip,rk3288-crypto`, `rockchip,rk3328-crypto`, `rockchip,rk3399-crypto`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (maxItems=4; minItems=3); `clock-names` (maxItems=4; minItems=3); `resets` (maxItems=3; minItems=1); `reset-names` (maxItems=3; minItems=1).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `rockchip,rk3288-crypto`, `rockchip,rk3328-crypto`, `rockchip,rk3399-crypto`; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/rockchip,rk3288-crypto.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (127 lines). Maintainers listed by the binding: `Heiko Stuebner <heiko@sntech.de>`.
