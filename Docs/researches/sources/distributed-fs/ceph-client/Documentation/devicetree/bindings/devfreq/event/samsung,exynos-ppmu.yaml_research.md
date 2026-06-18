# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/samsung,exynos-ppmu.yaml

## Purpose
Samsung Exynos SoC PPMU (Platform Performance Monitoring Unit) is a devfreq event counter binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `samsung,exynos-ppmu.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Samsung Exynos SoC has PPMU (Platform Performance Monitoring Unit) for each IP. PPMU provides the primitive values to get performance data. These PPMU events provide information of the SoC's behaviors so that you may use to analyze system performance, to make behaviors visible and to count usages of each IP (DMC...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/devfreq/event/samsung,exynos-ppmu.yaml#`, top-level `compatible` values `samsung,exynos-ppmu`, `samsung,exynos-ppmu-v2`, required properties `compatible`, `reg`, and top-level properties `compatible`, `clock-names`, `clocks`, `reg`, `events`.
Key property contracts include: `compatible` (enum `samsung,exynos-ppmu`, `samsung,exynos-ppmu-v2`); `clock-names` (declared by schema); `clocks` (maxItems=1); `reg` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include devfreq/event drivers that sample memory-controller or activity-monitor counters; driver matching through compatible strings such as `samsung,exynos-ppmu`, `samsung,exynos-ppmu-v2`; provider bindings for `clocks`, `clock-names`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/devfreq/event/samsung,exynos-ppmu.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is event/devfreq registration and nonzero activity counters under memory or device load
- schema contains 3 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (169 lines). Maintainers listed by the binding: `Chanwoo Choi <cw00.choi@samsung.com>`, `Krzysztof Kozlowski <krzk@kernel.org>`.
