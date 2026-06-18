# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/samsung-sss.yaml

## Purpose
Samsung Exynos SoC SSS (Security SubSystem) module is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `samsung-sss.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The SSS module in S5PV210 SoC supports the following: -- Feeder (FeedCtrl) -- Advanced Encryption Standard (AES) -- Data Encryption Standard (DES)/3DES -- Public Key Accelerator (PKA) -- SHA-1/SHA-256/MD5/HMAC (SHA-1/SHA-256/MD5)/PRNG -- PRNG: Pseudo Random Number Generator The SSS module in Exynos4 (Exynos4210) and...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/samsung-sss.yaml#`, top-level `compatible` values `samsung,s5pv210-secss`, `samsung,exynos4210-secss`, required properties `compatible`, `reg`, `clock-names`, `clocks`, `interrupts`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `clocks` (maxItems=1); `clock-names` (declared by schema); `interrupts` (maxItems=1; One feed control interrupt.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `samsung,s5pv210-secss`, `samsung,exynos4210-secss`; provider bindings for `clocks`, `clock-names`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/samsung-sss.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- add or update example nodes when changing required resources so validation covers the intended binding shape

## Source Notes
The source was read in full for this research pass (57 lines). Maintainers listed by the binding: `Krzysztof Kozlowski <krzk@kernel.org>`.
