# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-hash.yaml

## Purpose
STMicroelectronics STM32 HASH is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `st,stm32-hash.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The STM32 HASH block is built on the HASH block found in the STn8820 SoC introduced in 2007, and subsequently used in the U8500 SoC in 2010.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/st,stm32-hash.yaml#`, top-level `compatible` values `st,stn8820-hash`, `stericsson,ux500-hash`, `st,stm32f456-hash`, `st,stm32f756-hash`, `st,stm32mp13-hash`, required properties `compatible`, `reg`, `clocks`, and top-level properties `compatible`, `reg`, `clocks`, `interrupts`, `resets`, `dmas`, `dma-names`, `dma-maxburst`, `power-domains`, `access-controllers`.
Key property contracts include: `compatible` (enum `st,stn8820-hash`, `stericsson,ux500-hash`, `st,stm32f456-hash`, `st,stm32f756-hash`, `st,stm32mp13-hash`); `reg` (maxItems=1); `clocks` (maxItems=1); `interrupts` (maxItems=1); `resets` (maxItems=1); `dmas` (maxItems=1); `dma-names` (declared by schema); `power-domains` (maxItems=1).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `st,stn8820-hash`, `stericsson,ux500-hash`, `st,stm32f456-hash`, `st,stm32f756-hash`, and 1 more; provider bindings for `clocks`, `resets`, `interrupts`, `dmas`, `dma-names`, `power-domains`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/st,stm32-hash.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (94 lines). Maintainers listed by the binding: `Lionel Debieve <lionel.debieve@foss.st.com>`.
