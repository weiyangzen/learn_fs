# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec2.0.yaml

## Purpose
Freescale SoC SEC Security Engines versions 1.x-2.x-3.x is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,sec2.0.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Freescale SoC SEC Security Engines versions 1.x-2.x-3.x.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/fsl,sec2.0.yaml#`, top-level `compatible` values `fsl,sec3.3`, `fsl,sec3.1`, `fsl,sec3.0`, `fsl,sec2.4`, `fsl,sec2.2`, `fsl,sec2.1`, `fsl,sec2.0`, `fsl,sec1.2`, `fsl,sec1.0`, required properties `compatible`, `reg`, `fsl,num-channels`, `fsl,channel-fifo-len`, `fsl,exec-units-mask`, `fsl,descriptor-types-mask`, and top-level properties `compatible`, `reg`, `interrupts`, `fsl,num-channels`, `fsl,channel-fifo-len`, `fsl,exec-units-mask`, `fsl,descriptor-types-mask`.
Key property contracts include: `compatible` (Should contain entries for this and backward compatible SEC versions, high to low. Warning - SEC1 and SEC2 are mutually exclusive.); `reg` (maxItems=1); `interrupts` (maxItems=1); `fsl,num-channels` (enum `1`, `4`; ref `/schemas/types.yaml#/definitions/uint32`; An integer representing the number of channels available.); `fsl,channel-fifo-len` (ref `/schemas/types.yaml#/definitions/uint32`; An integer representing the number of descriptor pointers each channel fetch fifo can hold.); `fsl,exec-units-mask` (ref `/schemas/types.yaml#/definitions/uint32`; The bitmask representing what execution units (EUs) are available. EU information should be encoded following the SEC's Descriptor Header Dword EU_SEL0 field documentation, i.e. as follows: bit 0 = reserved - should be 0 bit 1 = set if SEC has the ARC4 EU (AFEU) bit 2 = set if SEC has the DES/3DES EU (DEU) bit 3 = s...); `fsl,descriptor-types-mask` (ref `/schemas/types.yaml#/definitions/uint32`; The bitmask representing what descriptors are available. Descriptor type information should be encoded following the SEC's Descriptor Header Dword DESC_TYPE field documentation, i.e. as follows: bit 0 = SEC supports descriptor type aesu_ctr_nonsnoop bit 1 = SEC supports descriptor type ipsec_esp bit 2 = SEC supports...).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `fsl,sec3.3`, `fsl,sec3.1`, `fsl,sec3.0`, `fsl,sec2.4`, and 5 more; provider bindings for `interrupts`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/fsl,sec2.0.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (144 lines). Maintainers listed by the binding: `J. Neuschäfer <j.ne@posteo.net>`.
