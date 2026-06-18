# Research: subset-b-000567

Grouped research for Linux DeviceTree crypto, devfreq, and display binding schemas in the Ceph client kernel source mirror. Each section preserves the source path and is bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec-v4.0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec-v4.0.yaml

## Purpose
Freescale SEC 4 is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,sec-v4.0.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. NOTE: the SEC 4 is also known as Freescale's Cryptographic Accelerator Accelerator and Assurance Module (CAAM). SEC 4 h/w can process requests from 2 types of sources. 1. DPAA Queue Interface (HW interface between Queue Manager & SEC 4). 2. Job Rings (HW interface between cores & SEC 4 registers). High Speed Data Pa...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/fsl,sec-v4.0.yaml#`, top-level `compatible` values `fsl,sec-v5.4`, `fsl,sec-v6.0`, `fsl,sec-v5.0`, `fsl,sec-v4.0`, `fsl,imx6ul-caam`, `fsl,imx8qm-caam`, `fsl,imx8qxp-caam`, required properties `compatible`, `reg`, `ranges`, and top-level properties `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`, `dma-coherent`, `interrupts`, `power-domains`, `fsl,sec-era`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `#address-cells` (enum `1`, `2`); `#size-cells` (enum `1`, `2`); `clocks` (maxItems=4; minItems=1); `clock-names` (maxItems=4; minItems=1); `interrupts` (maxItems=1); `power-domains` (maxItems=1); `fsl,sec-era` (ref `/schemas/types.yaml#/definitions/uint32`; Defines the 'ERA' of the SEC device.).
The schema also defines pattern properties `^jr@[0-9a-f]+$`, `^rtic@[0-9a-f]+$`, which describe child nodes or reusable node fragments.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `fsl,sec-v5.4`, `fsl,sec-v6.0`, `fsl,sec-v5.0`, `fsl,sec-v4.0`, and 3 more; provider bindings for `clocks`, `clock-names`, `interrupts`, `power-domains`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- DMA coherency must reflect the interconnect/MMU behavior; a wrong flag can cause subtle crypto data corruption

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/fsl,sec-v4.0.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (318 lines). Maintainers listed by the binding: `"Horia Geantă" <horia.geanta@nxp.com>`, `Pankaj Gupta <pankaj.gupta@nxp.com>`, `Gaurav Jain <gaurav.jain@nxp.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec-v4.0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec2.0.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl,sec2.0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-dcp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-dcp.yaml

## Purpose
Freescale DCP (Data Co-Processor) found on i.MX23/i.MX28 is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl-dcp.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Freescale DCP (Data Co-Processor) found on i.MX23/i.MX28.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/fsl-dcp.yaml#`, top-level `compatible` values `fsl,imx23-dcp`, `fsl,imx28-dcp`, `fsl,imx6sl-dcp`, `fsl,imx6ull-dcp`, required properties `compatible`, `reg`, `interrupts`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (minItems=2; Should contain MXS DCP interrupt numbers, VMI IRQ and DCP IRQ must be supplied, optionally Secure IRQ can be present, but is currently not implemented and not used.); `clocks` (maxItems=1); `clock-names` (const `dcp`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `fsl,imx23-dcp`, `fsl,imx28-dcp`, `fsl,imx6sl-dcp`, `fsl,imx6ull-dcp`; provider bindings for `clocks`, `clock-names`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/fsl-dcp.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (56 lines). Maintainers listed by the binding: `Marek Vasut <marex@denx.de>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-dcp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-imx-sahara.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-imx-sahara.yaml

## Purpose
Freescale SAHARA Cryptographic Accelerator is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl-imx-sahara.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Freescale SAHARA Cryptographic Accelerator.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/fsl-imx-sahara.yaml#`, top-level `compatible` values `fsl,imx27-sahara`, `fsl,imx53-sahara`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.
Key property contracts include: `compatible` (enum `fsl,imx27-sahara`, `fsl,imx53-sahara`); `reg` (maxItems=1); `interrupts` (minItems=1); `clocks` (declared by schema); `clock-names` (declared by schema).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `fsl,imx27-sahara`, `fsl,imx53-sahara`; provider bindings for `clocks`, `clock-names`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/fsl-imx-sahara.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (74 lines). Maintainers listed by the binding: `Steffen Trumtrar <s.trumtrar@pengutronix.de>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-imx-sahara.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-imx-scc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-imx-scc.yaml

## Purpose
Freescale Security Controller (SCC) is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl-imx-scc.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Freescale Security Controller (SCC).

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/fsl-imx-scc.yaml#`, top-level `compatible` values `fsl,imx25-scc`, required properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, and top-level properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`.
Key property contracts include: `compatible` (const `fsl,imx25-scc`); `reg` (maxItems=1); `interrupts` (declared by schema); `interrupt-names` (declared by schema); `clocks` (maxItems=1); `clock-names` (const `ipg`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `fsl,imx25-scc`; provider bindings for `clocks`, `clock-names`, `interrupts`, `interrupt-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/fsl-imx-scc.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (54 lines). Maintainers listed by the binding: `Steffen Trumtrar <s.trumtrar@pengutronix.de>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/fsl-imx-scc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/hisilicon,hip06-sec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/hisilicon,hip06-sec.yaml

## Purpose
Hisilicon hip06/hip07 Security Accelerator is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `hisilicon,hip06-sec.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Hisilicon hip06/hip07 Security Accelerator.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/hisilicon,hip06-sec.yaml#`, top-level `compatible` values `hisilicon,hip06-sec`, `hisilicon,hip07-sec`, required properties `compatible`, `reg`, `interrupts`, `dma-coherent`, and top-level properties `compatible`, `reg`, `interrupts`, `dma-coherent`, `iommus`.
Key property contracts include: `compatible` (enum `hisilicon,hip06-sec`, `hisilicon,hip07-sec`); `reg` (declared by schema); `interrupts` (declared by schema).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `hisilicon,hip06-sec`, `hisilicon,hip07-sec`; provider bindings for `interrupts`, `iommus`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- DMA coherency must reflect the interconnect/MMU behavior; a wrong flag can cause subtle crypto data corruption

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/hisilicon,hip06-sec.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (134 lines). Maintainers listed by the binding: `Jonathan Cameron <Jonathan.Cameron@huawei.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/hisilicon,hip06-sec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/img,hash-accelerator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/img,hash-accelerator.yaml

## Purpose
Imagination Technologies hardware hash accelerator is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `img,hash-accelerator.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The hash accelerator provides hardware hashing acceleration for SHA1, SHA224, SHA256 and MD5 hashes.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/img,hash-accelerator.yaml#`, top-level `compatible` values `img,hash-accelerator`, required properties `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`, and top-level properties `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`.
Key property contracts include: `compatible` (const `img,hash-accelerator`); `reg` (declared by schema); `interrupts` (maxItems=1); `dmas` (maxItems=1); `dma-names` (declared by schema); `clocks` (declared by schema); `clock-names` (declared by schema).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `img,hash-accelerator`; provider bindings for `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/img,hash-accelerator.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (69 lines). Maintainers listed by the binding: `James Hartley <james.hartley@imgtec.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/img,hash-accelerator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/inside-secure,safexcel-eip93.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/inside-secure,safexcel-eip93.yaml

## Purpose
Inside Secure SafeXcel EIP-93 cryptographic engine is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `inside-secure,safexcel-eip93.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Inside Secure SafeXcel EIP-93 is a cryptographic engine IP block integrated in varios devices with very different and generic name from PKTE to simply vendor+EIP93. The real IP under the hood is actually developed by Inside Secure and given to license to vendors. The IP block is sold with different model based o...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/inside-secure,safexcel-eip93.yaml#`, top-level `compatible` values `airoha,en7581-eip93`, `inside-secure,safexcel-eip93ies`, `inside-secure,safexcel-eip93i`, `inside-secure,safexcel-eip93ie`, `inside-secure,safexcel-eip93is`, `inside-secure,safexcel-eip93iw`, required properties `compatible`, `reg`, `interrupts`, and top-level properties `compatible`, `reg`, `interrupts`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `airoha,en7581-eip93`, `inside-secure,safexcel-eip93ies`, `inside-secure,safexcel-eip93i`, `inside-secure,safexcel-eip93ie`, and 2 more; provider bindings for `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/inside-secure,safexcel-eip93.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (67 lines). Maintainers listed by the binding: `Christian Marangi <ansuelsmth@gmail.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/inside-secure,safexcel-eip93.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/inside-secure,safexcel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/inside-secure,safexcel.yaml

## Purpose
Inside Secure SafeXcel cryptographic engine is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `inside-secure,safexcel.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Inside Secure SafeXcel cryptographic engine.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/inside-secure,safexcel.yaml#`, top-level `compatible` values `marvell,armada-cp110-crypto`, `inside-secure,safexcel-eip197b`, `marvell,armada-3700-crypto`, `mediatek,mt7981-crypto`, `mediatek,mt7986-crypto`, `inside-secure,safexcel-eip97ies`, `inside-secure,safexcel-eip197d`, `inside-secure,safexcel-eip197`, `inside-secure,safexcel-eip97`, required properties `reg`, `interrupts`, `interrupt-names`, and top-level properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `dma-coherent`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=6; minItems=4); `interrupt-names` (minItems=4); `clocks` (maxItems=2; minItems=1); `clock-names` (minItems=1).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `marvell,armada-cp110-crypto`, `inside-secure,safexcel-eip197b`, `marvell,armada-3700-crypto`, `mediatek,mt7981-crypto`, and 5 more; provider bindings for `clocks`, `clock-names`, `interrupts`, `interrupt-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- DMA coherency must reflect the interconnect/MMU behavior; a wrong flag can cause subtle crypto data corruption

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/inside-secure,safexcel.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (113 lines). Maintainers listed by the binding: `Antoine Tenart <atenart@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/inside-secure,safexcel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,ixp4xx-crypto.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,ixp4xx-crypto.yaml

## Purpose
Intel IXP4xx cryptographic engine is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `intel,ixp4xx-crypto.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Intel IXP4xx cryptographic engine makes use of the IXP4xx NPE (Network Processing Engine). Since it is not a device on its own it is defined as a subnode of the NPE, if crypto support is available on the platform.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/intel,ixp4xx-crypto.yaml#`, top-level `compatible` values `intel,ixp4xx-crypto`, required properties `compatible`, `intel,npe-handle`, `queue-rx`, `queue-txready`, and top-level properties `compatible`, `intel,npe-handle`, `queue-rx`, `queue-txready`.
Key property contracts include: `compatible` (const `intel,ixp4xx-crypto`); `intel,npe-handle` (ref `/schemas/types.yaml#/definitions/phandle-array`; phandle to the NPE this crypto engine is using, the cell describing the NPE instance to be used.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `intel,ixp4xx-crypto`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle-array`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/intel,ixp4xx-crypto.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- add or update example nodes when changing required resources so validation covers the intended binding shape

## Source Notes
The source was read in full for this research pass (56 lines). Maintainers listed by the binding: `Linus Walleij <linusw@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,ixp4xx-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-aes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-aes.yaml

## Purpose
Intel Keem Bay OCS AES is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `intel,keembay-ocs-aes.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Intel Keem Bay Offload and Crypto Subsystem (OCS) AES engine provides hardware-accelerated AES/SM4 encryption/decryption.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/intel,keembay-ocs-aes.yaml#`, top-level `compatible` values `intel,keembay-ocs-aes`, required properties `compatible`, `reg`, `interrupts`, `clocks`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`.
Key property contracts include: `compatible` (const `intel,keembay-ocs-aes`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `intel,keembay-ocs-aes`; provider bindings for `clocks`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/intel,keembay-ocs-aes.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (45 lines). Maintainers listed by the binding: `Daniele Alessandrelli <daniele.alessandrelli@intel.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-aes.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-ecc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-ecc.yaml

## Purpose
Intel Keem Bay OCS ECC is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `intel,keembay-ocs-ecc.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Intel Keem Bay Offload and Crypto Subsystem (OCS) Elliptic Curve Cryptography (ECC) device provides hardware acceleration for elliptic curve cryptography using the NIST P-256 and NIST P-384 elliptic curves.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/intel,keembay-ocs-ecc.yaml#`, top-level `compatible` values `intel,keembay-ocs-ecc`, required properties `compatible`, `reg`, `interrupts`, `clocks`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`.
Key property contracts include: `compatible` (const `intel,keembay-ocs-ecc`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `intel,keembay-ocs-ecc`; provider bindings for `clocks`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/intel,keembay-ocs-ecc.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (47 lines). Maintainers listed by the binding: `Daniele Alessandrelli <daniele.alessandrelli@intel.com>`, `Prabhjot Khurana <prabhjot.khurana@intel.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-ecc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-hcu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-hcu.yaml

## Purpose
Intel Keem Bay OCS HCU is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `intel,keembay-ocs-hcu.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Intel Keem Bay Offload and Crypto Subsystem (OCS) Hash Control Unit (HCU) provides hardware-accelerated hashing and HMAC.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/intel,keembay-ocs-hcu.yaml#`, top-level `compatible` values `intel,keembay-ocs-hcu`, required properties `compatible`, `reg`, `interrupts`, `clocks`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`.
Key property contracts include: `compatible` (const `intel,keembay-ocs-hcu`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `intel,keembay-ocs-hcu`; provider bindings for `clocks`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/intel,keembay-ocs-hcu.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (46 lines). Maintainers listed by the binding: `Declan Murphy <declan.murphy@intel.com>`, `Daniele Alessandrelli <daniele.alessandrelli@intel.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/intel,keembay-ocs-hcu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/marvell,orion-crypto.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/marvell,orion-crypto.yaml

## Purpose
Marvell Cryptographic Engines And Security Accelerator is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `marvell,orion-crypto.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. Marvell Cryptographic Engines And Security Accelerator

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/marvell,orion-crypto.yaml#`, top-level `compatible` values `marvell,armada-370-crypto`, `marvell,armada-xp-crypto`, `marvell,armada-375-crypto`, `marvell,armada-38x-crypto`, `marvell,dove-crypto`, `marvell,kirkwood-crypto`, `marvell,orion-crypto`, required properties `compatible`, `reg`, `reg-names`, `interrupts`, `marvell,crypto-srams`, and top-level properties `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `marvell,crypto-srams`, `marvell,crypto-sram-size`.
Key property contracts include: `compatible` (enum `marvell,armada-370-crypto`, `marvell,armada-xp-crypto`, `marvell,armada-375-crypto`, `marvell,armada-38x-crypto`, `marvell,dove-crypto`, `marvell,kirkwood-crypto`, `marvell,orion-crypto`); `reg` (minItems=1); `interrupts` (maxItems=2; minItems=1; One interrupt for each CESA engine); `clocks` (maxItems=4; minItems=1; One or two clocks for each CESA engine); `clock-names` (minItems=1); `marvell,crypto-srams` (maxItems=2; minItems=1; ref `/schemas/types.yaml#/definitions/phandle-array`; Phandle(s) to crypto SRAM.); `marvell,crypto-sram-size` (ref `/schemas/types.yaml#/definitions/uint32`; SRAM size reserved for crypto operations.).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `marvell,armada-370-crypto`, `marvell,armada-xp-crypto`, `marvell,armada-375-crypto`, `marvell,armada-38x-crypto`, and 3 more; provider bindings for `clocks`, `clock-names`, `interrupts`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/marvell,orion-crypto.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (133 lines). Maintainers listed by the binding: `Andrew Lunn <andrew@lunn.ch>`, `Boris Brezillon <bbrezillon@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/marvell,orion-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/nvidia,tegra234-se-aes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/nvidia,tegra234-se-aes.yaml

## Purpose
NVIDIA Tegra Security Engine for AES algorithms is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `nvidia,tegra234-se-aes.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Tegra Security Engine accelerates the following AES encryption/decryption algorithms - AES-ECB, AES-CBC, AES-OFB, AES-XTS, AES-CTR, AES-GCM, AES-CCM, AES-CMAC

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/nvidia,tegra234-se-aes.yaml#`, top-level `compatible` values `nvidia,tegra234-se-aes`, required properties `compatible`, `reg`, `clocks`, `iommus`, and top-level properties `compatible`, `reg`, `clocks`, `iommus`, `dma-coherent`.
Key property contracts include: `compatible` (const `nvidia,tegra234-se-aes`); `reg` (maxItems=1); `clocks` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `nvidia,tegra234-se-aes`; provider bindings for `clocks`, `iommus`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- DMA coherency must reflect the interconnect/MMU behavior; a wrong flag can cause subtle crypto data corruption

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/nvidia,tegra234-se-aes.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (52 lines). Maintainers listed by the binding: `Akhil R <akhilrajeev@nvidia.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/nvidia,tegra234-se-aes.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/nvidia,tegra234-se-hash.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/nvidia,tegra234-se-hash.yaml

## Purpose
NVIDIA Tegra Security Engine for HASH algorithms is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `nvidia,tegra234-se-hash.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Tegra Security HASH Engine accelerates the following HASH functions - SHA1, SHA224, SHA256, SHA384, SHA512, SHA3-224, SHA3-256, SHA3-384, SHA3-512 HMAC(SHA224), HMAC(SHA256), HMAC(SHA384), HMAC(SHA512)

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/nvidia,tegra234-se-hash.yaml#`, top-level `compatible` values `nvidia,tegra234-se-hash`, required properties `compatible`, `reg`, `clocks`, `iommus`, and top-level properties `compatible`, `reg`, `clocks`, `iommus`, `dma-coherent`.
Key property contracts include: `compatible` (const `nvidia,tegra234-se-hash`); `reg` (maxItems=1); `clocks` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `nvidia,tegra234-se-hash`; provider bindings for `clocks`, `iommus`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- DMA coherency must reflect the interconnect/MMU behavior; a wrong flag can cause subtle crypto data corruption

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/nvidia,tegra234-se-hash.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (52 lines). Maintainers listed by the binding: `Akhil R <akhilrajeev@nvidia.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/nvidia,tegra234-se-hash.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom,inline-crypto-engine.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom,inline-crypto-engine.yaml

## Purpose
Qualcomm Technologies, Inc. (QTI) Inline Crypto Engine is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `qcom,inline-crypto-engine.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Qualcomm Technologies, Inc. (QTI) Inline Crypto Engine.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/qcom,inline-crypto-engine.yaml#`, top-level `compatible` values `qcom,eliza-inline-crypto-engine`, `qcom,kaanapali-inline-crypto-engine`, `qcom,milos-inline-crypto-engine`, `qcom,qcs8300-inline-crypto-engine`, `qcom,sa8775p-inline-crypto-engine`, `qcom,sc7180-inline-crypto-engine`, `qcom,sc7280-inline-crypto-engine`, `qcom,sm8450-inline-crypto-engine`, `qcom,sm8550-inline-crypto-engine`, `qcom,sm8650-inline-crypto-engine`, `qcom,sm8750-inline-crypto-engine`, `qcom,inline-crypto-engine`, required properties `compatible`, `reg`, `clocks`, and top-level properties `compatible`, `reg`, `clocks`, `operating-points-v2`, `opp-table`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `clocks` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `qcom,eliza-inline-crypto-engine`, `qcom,kaanapali-inline-crypto-engine`, `qcom,milos-inline-crypto-engine`, `qcom,qcs8300-inline-crypto-engine`, and 8 more; provider bindings for `clocks`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/qcom,inline-crypto-engine.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (78 lines). Maintainers listed by the binding: `Bjorn Andersson <andersson@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom,inline-crypto-engine.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom,prng.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom,prng.yaml

## Purpose
Qualcomm Pseudo Random Number Generator is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `qcom,prng.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Qualcomm Pseudo Random Number Generator.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/qcom,prng.yaml#`, top-level `compatible` values `qcom,prng`, `qcom,prng-ee`, `qcom,ipq5332-trng`, `qcom,ipq5424-trng`, `qcom,ipq9574-trng`, `qcom,kaanapali-trng`, `qcom,milos-trng`, `qcom,qcs615-trng`, `qcom,qcs8300-trng`, `qcom,sa8255p-trng`, `qcom,sa8775p-trng`, `qcom,sc7280-trng`, `qcom,sm8450-trng`, `qcom,sm8550-trng`, and 4 more, required properties `compatible`, `reg`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `clocks` (maxItems=1); `clock-names` (declared by schema).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `qcom,prng`, `qcom,prng-ee`, `qcom,ipq5332-trng`, `qcom,ipq5424-trng`, and 14 more; provider bindings for `clocks`, `clock-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/qcom,prng.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (72 lines). Maintainers listed by the binding: `Vinod Koul <vkoul@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom,prng.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom-qce.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom-qce.yaml

## Purpose
Qualcomm crypto engine driver is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `qcom-qce.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. This document defines the binding for the QCE crypto controller found on Qualcomm parts.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/qcom-qce.yaml#`, top-level `compatible` values `qcom,crypto-v5.1`, `qcom,crypto-v5.4`, `qcom,ipq4019-qce`, `qcom,sm8150-qce`, `qcom,qce`, `qcom,ipq6018-qce`, `qcom,ipq8074-qce`, `qcom,ipq9574-qce`, `qcom,msm8996-qce`, `qcom,qcm2290-qce`, `qcom,sdm845-qce`, `qcom,sm6115-qce`, `qcom,kaanapali-qce`, `qcom,qcs615-qce`, and 11 more, required properties `compatible`, `reg`, `dmas`, `dma-names`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`, `dmas`, `dma-names`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `clocks` (maxItems=3; minItems=1); `clock-names` (maxItems=3; minItems=1); `dmas` (declared by schema); `dma-names` (declared by schema).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `qcom,crypto-v5.1`, `qcom,crypto-v5.4`, `qcom,ipq4019-qce`, `qcom,sm8150-qce`, and 21 more; provider bindings for `clocks`, `clock-names`, `dmas`, `dma-names`, `iommus`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/qcom-qce.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (178 lines). Maintainers listed by the binding: `Bjorn Andersson <andersson@kernel.org>`, `Konrad Dybcio <konradybcio@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom-qce.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/rockchip,rk3288-crypto.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/rockchip,rk3288-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/samsung-slimsss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/samsung-slimsss.yaml

## Purpose
Samsung Exynos SoC SlimSSS (Slim Security SubSystem) module is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `samsung-slimsss.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The SlimSSS module in Exynos5433 SoC supports the following: -- Feeder (FeedCtrl) -- Advanced Encryption Standard (AES) with ECB,CBC,CTR,XTS and (CBC/XTS)/CTS -- SHA-1/SHA-256 and (SHA-1/SHA-256)/HMAC

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/samsung-slimsss.yaml#`, top-level `compatible` values `samsung,exynos5433-slim-sss`, required properties `compatible`, `reg`, `clock-names`, `clocks`, `interrupts`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `clocks` (maxItems=2); `clock-names` (declared by schema); `interrupts` (maxItems=1; One feed control interrupt.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `samsung,exynos5433-slim-sss`; provider bindings for `clocks`, `clock-names`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/samsung-slimsss.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- add or update example nodes when changing required resources so validation covers the intended binding shape

## Source Notes
The source was read in full for this research pass (45 lines). Maintainers listed by the binding: `Krzysztof Kozlowski <krzk@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/samsung-slimsss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/samsung-sss.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/samsung-sss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-crc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-crc.yaml

## Purpose
STMicroelectronics STM32 CRC is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `st,stm32-crc.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for STMicroelectronics STM32 CRC.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/st,stm32-crc.yaml#`, top-level `compatible` values `st,stm32f7-crc`, required properties `compatible`, `reg`, `clocks`, and top-level properties `compatible`, `reg`, `clocks`.
Key property contracts include: `compatible` (const `st,stm32f7-crc`); `reg` (maxItems=1); `clocks` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `st,stm32f7-crc`; provider bindings for `clocks`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/st,stm32-crc.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (38 lines). Maintainers listed by the binding: `Lionel Debieve <lionel.debieve@foss.st.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-crc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-cryp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-cryp.yaml

## Purpose
STMicroelectronics STM32 CRYP is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `st,stm32-cryp.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The STM32 CRYP block is built on the CRYP block found in the STn8820 SoC introduced in 2007, and subsequently used in the U8500 SoC in 2010.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/st,stm32-cryp.yaml#`, top-level `compatible` values `st,stn8820-cryp`, `stericsson,ux500-cryp`, `st,stm32f756-cryp`, `st,stm32mp1-cryp`, required properties `compatible`, `reg`, `clocks`, `interrupts`, and top-level properties `compatible`, `reg`, `clocks`, `interrupts`, `resets`, `dmas`, `dma-names`, `power-domains`, `access-controllers`.
Key property contracts include: `compatible` (enum `st,stn8820-cryp`, `stericsson,ux500-cryp`, `st,stm32f756-cryp`, `st,stm32mp1-cryp`); `reg` (maxItems=1); `clocks` (maxItems=1); `interrupts` (maxItems=1); `resets` (maxItems=1); `dmas` (declared by schema); `dma-names` (declared by schema); `power-domains` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `st,stn8820-cryp`, `stericsson,ux500-cryp`, `st,stm32f756-cryp`, `st,stm32mp1-cryp`; provider bindings for `clocks`, `resets`, `interrupts`, `dmas`, `dma-names`, `power-domains`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/st,stm32-cryp.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (74 lines). Maintainers listed by the binding: `Lionel Debieve <lionel.debieve@foss.st.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-cryp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-hash.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/st,stm32-hash.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/starfive,jh7110-crypto.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/starfive,jh7110-crypto.yaml

## Purpose
StarFive Cryptographic Module is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `starfive,jh7110-crypto.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for StarFive Cryptographic Module.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/starfive,jh7110-crypto.yaml#`, top-level `compatible` values `starfive,jh7110-crypto`, `starfive,jh8100-crypto`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `resets`, `dmas`, `dma-names`.
Key property contracts include: `compatible` (enum `starfive,jh7110-crypto`, `starfive,jh8100-crypto`); `reg` (maxItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `interrupts` (minItems=1); `resets` (maxItems=1); `dmas` (declared by schema); `dma-names` (declared by schema).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `starfive,jh7110-crypto`, `starfive,jh8100-crypto`; provider bindings for `clocks`, `clock-names`, `resets`, `interrupts`, `dmas`, `dma-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/starfive,jh7110-crypto.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (96 lines). Maintainers listed by the binding: `Jia Jie Ho <jiajie.ho@starfivetech.com>`, `William Qiu <william.qiu@starfivetech.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/starfive,jh7110-crypto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,am62l-dthev2.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,am62l-dthev2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap-sham.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap-sham.yaml

## Purpose
OMAP SoC SHA crypto Module is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ti,omap-sham.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for OMAP SoC SHA crypto Module.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/ti,omap-sham.yaml#`, top-level `compatible` values `ti,omap2-sham`, `ti,omap4-sham`, `ti,omap5-sham`, required properties `compatible`, `ti,hwmods`, `reg`, `interrupts`, and top-level properties `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `ti,hwmods`.
Key property contracts include: `compatible` (enum `ti,omap2-sham`, `ti,omap4-sham`, `ti,omap5-sham`); `reg` (maxItems=1); `interrupts` (maxItems=1); `dmas` (maxItems=1); `dma-names` (const `rx`); `ti,hwmods` (enum `sham`; ref `/schemas/types.yaml#/definitions/string`; Name of the hwmod associated with the SHAM module).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `ti,omap2-sham`, `ti,omap4-sham`, `ti,omap5-sham`; provider bindings for `interrupts`, `dmas`, `dma-names`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/string`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/ti,omap-sham.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (56 lines). Maintainers listed by the binding: `Animesh Agarwal <animeshagarwal28@gmail.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap-sham.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap2-aes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap2-aes.yaml

## Purpose
OMAP SoC AES crypto Module is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ti,omap2-aes.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for OMAP SoC AES crypto Module.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/ti,omap2-aes.yaml#`, top-level `compatible` values `ti,omap2-aes`, `ti,omap3-aes`, `ti,omap4-aes`, required properties `compatible`, `reg`, `interrupts`, and top-level properties `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `ti,hwmods`.
Key property contracts include: `compatible` (enum `ti,omap2-aes`, `ti,omap3-aes`, `ti,omap4-aes`); `reg` (maxItems=1); `interrupts` (maxItems=1); `dmas` (maxItems=2); `dma-names` (declared by schema); `ti,hwmods` (const `aes`; Name of the hwmod associated with the AES module).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `ti,omap2-aes`, `ti,omap3-aes`, `ti,omap4-aes`; provider bindings for `interrupts`, `dmas`, `dma-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/ti,omap2-aes.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (58 lines). Maintainers listed by the binding: `Aaro Koskinen <aaro.koskinen@iki.fi>`, `Andreas Kemnade <andreas@kemnade.info>`, `Kevin Hilman <khilman@baylibre.com>`, `Roger Quadros <rogerq@kernel.org>`, `Tony Lindgren <tony@atomide.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap2-aes.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap4-des.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap4-des.yaml

## Purpose
OMAP4 DES crypto Module is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ti,omap4-des.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for OMAP4 DES crypto Module.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/ti,omap4-des.yaml#`, top-level `compatible` values `ti,omap4-des`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, and top-level properties `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`.
Key property contracts include: `compatible` (const `ti,omap4-des`); `reg` (maxItems=1); `interrupts` (maxItems=1); `dmas` (maxItems=2); `dma-names` (declared by schema); `clocks` (maxItems=1); `clock-names` (declared by schema).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `ti,omap4-des`; provider bindings for `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/ti,omap4-des.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (65 lines). Maintainers listed by the binding: `Aaro Koskinen <aaro.koskinen@iki.fi>`, `Andreas Kemnade <andreas@kemnade.info>`, `Kevin Hilman <khilman@baylibre.com>`, `Roger Quadros <rogerq@kernel.org>`, `Tony Lindgren <tony@atomide.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,omap4-des.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,sa2ul.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,sa2ul.yaml

## Purpose
K3 SoC SA2UL crypto module is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ti,sa2ul.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for K3 SoC SA2UL crypto module.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/ti,sa2ul.yaml#`, top-level `compatible` values `ti,j721e-sa2ul`, `ti,am654-sa2ul`, `ti,am64-sa2ul`, `ti,am62-sa3ul`, required properties `compatible`, `reg`, `dmas`, `dma-names`, and top-level properties `compatible`, `reg`, `power-domains`, `dmas`, `dma-names`, `#address-cells`, `#size-cells`, `ranges`, `clocks`, `clock-names`.
Key property contracts include: `compatible` (enum `ti,j721e-sa2ul`, `ti,am654-sa2ul`, `ti,am64-sa2ul`, `ti,am62-sa3ul`); `reg` (maxItems=1); `power-domains` (maxItems=1); `dmas` (declared by schema); `dma-names` (declared by schema); `#address-cells` (const `2`); `#size-cells` (const `2`); `clocks` (declared by schema); `clock-names` (declared by schema).
The schema also defines pattern properties `^rng@[a-f0-9]+$`, which describe child nodes or reusable node fragments.
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `ti,j721e-sa2ul`, `ti,am654-sa2ul`, `ti,am64-sa2ul`, `ti,am62-sa3ul`; provider bindings for `clocks`, `clock-names`, `dmas`, `dma-names`, `power-domains`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/ti,sa2ul.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (98 lines). Maintainers listed by the binding: `Tero Kristo <t-kristo@ti.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/ti,sa2ul.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/xlnx,versal-trng.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/xlnx,versal-trng.yaml

## Purpose
Xilinx Versal True Random Number Generator Hardware Accelerator is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `xlnx,versal-trng.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Versal True Random Number Generator consists of Ring Oscillators as entropy source and a deterministic CTR_DRBG random bit generator (DRBG).

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/xlnx,versal-trng.yaml#`, top-level `compatible` values `xlnx,versal-trng`, required properties `reg`, and top-level properties `compatible`, `reg`.
Key property contracts include: `compatible` (const `xlnx,versal-trng`); `reg` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `xlnx,versal-trng`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/xlnx,versal-trng.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (35 lines). Maintainers listed by the binding: `Harsh Jain <h.jain@amd.com>`, `Mounika Botcha <mounika.botcha@amd.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/xlnx,versal-trng.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/xlnx,zynqmp-aes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/xlnx,zynqmp-aes.yaml

## Purpose
Xilinx ZynqMP AES-GCM Hardware Accelerator is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `xlnx,zynqmp-aes.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The ZynqMP AES-GCM hardened cryptographic accelerator is used to encrypt or decrypt the data with provided key and initialization vector.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/xlnx,zynqmp-aes.yaml#`, top-level `compatible` values `xlnx,zynqmp-aes`, required properties `compatible`, and top-level properties `compatible`.
Key property contracts include: `compatible` (const `xlnx,zynqmp-aes`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `xlnx,zynqmp-aes`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/xlnx,zynqmp-aes.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (39 lines). Maintainers listed by the binding: `Kalyani Akula <kalyani.akula@amd.com>`, `Michal Simek <michal.simek@amd.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/xlnx,zynqmp-aes.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/rockchip,dfi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/rockchip,dfi.yaml

## Purpose
Rockchip DFI is a devfreq event counter binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `rockchip,dfi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Rockchip DFI.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/devfreq/event/rockchip,dfi.yaml#`, top-level `compatible` values `rockchip,rk3399-dfi`, `rockchip,rk3568-dfi`, `rockchip,rk3588-dfi`, required properties `compatible`, `interrupts`, `reg`, and top-level properties `compatible`, `clocks`, `clock-names`, `interrupts`, `reg`, `rockchip,pmu`.
Key property contracts include: `compatible` (enum `rockchip,rk3399-dfi`, `rockchip,rk3568-dfi`, `rockchip,rk3588-dfi`); `clocks` (maxItems=1); `clock-names` (declared by schema); `interrupts` (maxItems=4; minItems=1); `reg` (maxItems=1); `rockchip,pmu` (ref `/schemas/types.yaml#/definitions/phandle`; Phandle to the syscon managing the "PMU general register files".).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include devfreq/event drivers that sample memory-controller or activity-monitor counters; driver matching through compatible strings such as `rockchip,rk3399-dfi`, `rockchip,rk3568-dfi`, `rockchip,rk3588-dfi`; provider bindings for `clocks`, `clock-names`, `interrupts`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/devfreq/event/rockchip,dfi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is event/devfreq registration and nonzero activity counters under memory or device load
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (74 lines). Maintainers listed by the binding: `Sascha Hauer <s.hauer@pengutronix.de>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/rockchip,dfi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/samsung,exynos-nocp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/samsung,exynos-nocp.yaml

## Purpose
Samsung Exynos NoC (Network on Chip) Probe is a devfreq event counter binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `samsung,exynos-nocp.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Samsung Exynos542x SoC has a NoC (Network on Chip) Probe for NoC bus. NoC provides the primitive values to get the performance data. The packets that the Network on Chip (NoC) probes detects are transported over the network infrastructure to observer units. You can configure probes to capture packets with header...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/devfreq/event/samsung,exynos-nocp.yaml#`, top-level `compatible` values `samsung,exynos5420-nocp`, required properties `compatible`, `reg`, and top-level properties `compatible`, `clock-names`, `clocks`, `reg`.
Key property contracts include: `compatible` (const `samsung,exynos5420-nocp`); `clock-names` (declared by schema); `clocks` (maxItems=1); `reg` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include devfreq/event drivers that sample memory-controller or activity-monitor counters; driver matching through compatible strings such as `samsung,exynos5420-nocp`; provider bindings for `clocks`, `clock-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/devfreq/event/samsung,exynos-nocp.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is event/devfreq registration and nonzero activity counters under memory or device load
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (48 lines). Maintainers listed by the binding: `Chanwoo Choi <cw00.choi@samsung.com>`, `Krzysztof Kozlowski <krzk@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/samsung,exynos-nocp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/samsung,exynos-ppmu.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/event/samsung,exynos-ppmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/nvidia,tegra30-actmon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/nvidia,tegra30-actmon.yaml

## Purpose
NVIDIA Tegra30 Activity Monitor is a devfreq monitor binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `nvidia,tegra30-actmon.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The activity monitor block collects statistics about the behaviour of other components in the system. This information can be used to derive the rate at which the external memory needs to be clocked in order to serve all requests from the monitored clients.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/devfreq/nvidia,tegra30-actmon.yaml#`, top-level `compatible` values `nvidia,tegra30-actmon`, `nvidia,tegra114-actmon`, `nvidia,tegra124-actmon`, `nvidia,tegra210-actmon`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `interconnects`, `interconnect-names`, `operating-points-v2`, `#cooling-cells`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `interconnects`, `interconnect-names`, `operating-points-v2`, `#cooling-cells`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `clocks` (maxItems=2); `clock-names` (declared by schema); `resets` (maxItems=1); `reset-names` (declared by schema); `interrupts` (maxItems=1); `#cooling-cells` (const `2`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include devfreq/event drivers that sample memory-controller or activity-monitor counters; driver matching through compatible strings such as `nvidia,tegra30-actmon`, `nvidia,tegra114-actmon`, `nvidia,tegra124-actmon`, `nvidia,tegra210-actmon`; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/devfreq/nvidia,tegra30-actmon.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is event/devfreq registration and nonzero activity counters under memory or device load
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (129 lines). Maintainers listed by the binding: `Dmitry Osipenko <digetx@gmail.com>`, `Jon Hunter <jonathanh@nvidia.com>`, `Thierry Reding <thierry.reding@gmail.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/nvidia,tegra30-actmon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-backend.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-backend.yaml

## Purpose
Allwinner A10 Display Engine Backend is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun4i-a10-display-backend.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The display engine backend exposes layers and sprites to the system.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun4i-a10-display-backend.yaml#`, top-level `compatible` values `allwinner,sun4i-a10-display-backend`, `allwinner,sun5i-a13-display-backend`, `allwinner,sun6i-a31-display-backend`, `allwinner,sun7i-a20-display-backend`, `allwinner,sun8i-a23-display-backend`, `allwinner,sun8i-a33-display-backend`, `allwinner,sun9i-a80-display-backend`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `ports`, and top-level properties `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `interconnects`, `interconnect-names`, `ports`.
Key property contracts include: `compatible` (enum `allwinner,sun4i-a10-display-backend`, `allwinner,sun5i-a13-display-backend`, `allwinner,sun6i-a31-display-backend`, `allwinner,sun7i-a20-display-backend`, `allwinner,sun8i-a23-display-backend`, `allwinner,sun8i-a33-display-backend`, `allwinner,sun9i-a80-display-backend`); `reg` (minItems=1); `interrupts` (maxItems=1); `clocks` (minItems=3); `clock-names` (minItems=3); `resets` (minItems=1); `reset-names` (minItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun4i-a10-display-backend`, `allwinner,sun5i-a13-display-backend`, `allwinner,sun6i-a31-display-backend`, `allwinner,sun7i-a20-display-backend`, and 3 more; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-backend.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 2 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (272 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-backend.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-engine.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-engine.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-frontend.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-frontend.yaml

## Purpose
Allwinner A10 Display Engine Frontend is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun4i-a10-display-frontend.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The display engine frontend does formats conversion, scaling, deinterlacing and color space conversion.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun4i-a10-display-frontend.yaml#`, top-level `compatible` values `allwinner,sun4i-a10-display-frontend`, `allwinner,sun5i-a13-display-frontend`, `allwinner,sun6i-a31-display-frontend`, `allwinner,sun7i-a20-display-frontend`, `allwinner,sun8i-a23-display-frontend`, `allwinner,sun8i-a33-display-frontend`, `allwinner,sun9i-a80-display-frontend`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `ports`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `interconnects`, `interconnect-names`, `resets`, `ports`.
Key property contracts include: `compatible` (enum `allwinner,sun4i-a10-display-frontend`, `allwinner,sun5i-a13-display-frontend`, `allwinner,sun6i-a31-display-frontend`, `allwinner,sun7i-a20-display-frontend`, `allwinner,sun8i-a23-display-frontend`, `allwinner,sun8i-a33-display-frontend`, `allwinner,sun9i-a80-display-frontend`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `resets` (maxItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun4i-a10-display-frontend`, `allwinner,sun5i-a13-display-frontend`, `allwinner,sun6i-a31-display-frontend`, `allwinner,sun7i-a20-display-frontend`, and 3 more; provider bindings for `clocks`, `clock-names`, `resets`, `interrupts`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-frontend.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (124 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-display-frontend.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-hdmi.yaml

## Purpose
Allwinner A10 HDMI Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun4i-a10-hdmi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The HDMI Encoder supports the HDMI video and audio outputs, and does CEC. It is one end of the pipeline.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun4i-a10-hdmi.yaml#`, top-level `compatible` values `allwinner,sun4i-a10-hdmi`, `allwinner,sun5i-a10s-hdmi`, `allwinner,sun6i-a31-hdmi`, `allwinner,sun7i-a20-hdmi`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `dmas`, `dma-names`, `ports`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `resets` (maxItems=1); `dmas` (declared by schema); `dma-names` (declared by schema); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun4i-a10-hdmi`, `allwinner,sun5i-a10s-hdmi`, `allwinner,sun6i-a31-hdmi`, `allwinner,sun7i-a20-hdmi`; provider bindings for `clocks`, `clock-names`, `resets`, `interrupts`, `dmas`, `dma-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun4i-a10-hdmi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (170 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-tcon.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-tcon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-tv-encoder.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-tv-encoder.yaml

## Purpose
Allwinner A10 TV Encoder is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun4i-a10-tv-encoder.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Allwinner A10 TV Encoder.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun4i-a10-tv-encoder.yaml#`, top-level `compatible` values `allwinner,sun4i-a10-tv-encoder`, required properties `compatible`, `reg`, `clocks`, `resets`, `port`, and top-level properties `compatible`, `reg`, `clocks`, `resets`, `port`.
Key property contracts include: `compatible` (const `allwinner,sun4i-a10-tv-encoder`); `reg` (maxItems=1); `clocks` (maxItems=1); `resets` (maxItems=1); `port` (ref `/schemas/graph.yaml#/properties/port`; The first port should be the input endpoint, usually coming from the associated TCON.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun4i-a10-tv-encoder`; provider bindings for `clocks`, `resets`, `port`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun4i-a10-tv-encoder.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (56 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun4i-a10-tv-encoder.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun6i-a31-drc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun6i-a31-drc.yaml

## Purpose
Allwinner A31 Dynamic Range Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun6i-a31-drc.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The DRC (Dynamic Range Controller) allows to dynamically adjust pixel brightness/contrast based on histogram measurements for LCD content adaptive backlight control.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun6i-a31-drc.yaml#`, top-level `compatible` values `allwinner,sun6i-a31-drc`, `allwinner,sun6i-a31s-drc`, `allwinner,sun8i-a23-drc`, `allwinner,sun8i-a33-drc`, `allwinner,sun9i-a80-drc`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `ports`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `ports`.
Key property contracts include: `compatible` (enum `allwinner,sun6i-a31-drc`, `allwinner,sun6i-a31s-drc`, `allwinner,sun8i-a23-drc`, `allwinner,sun8i-a33-drc`, `allwinner,sun9i-a80-drc`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `resets` (maxItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun6i-a31-drc`, `allwinner,sun6i-a31s-drc`, `allwinner,sun8i-a23-drc`, `allwinner,sun8i-a33-drc`, and 1 more; provider bindings for `clocks`, `clock-names`, `resets`, `interrupts`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun6i-a31-drc.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (124 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun6i-a31-drc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun6i-a31-mipi-dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun6i-a31-mipi-dsi.yaml

## Purpose
Allwinner A31 MIPI-DSI Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun6i-a31-mipi-dsi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Allwinner A31 MIPI-DSI Controller.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun6i-a31-mipi-dsi.yaml#`, top-level `compatible` values `allwinner,sun6i-a31-mipi-dsi`, `allwinner,sun50i-a64-mipi-dsi`, `allwinner,sun50i-a100-mipi-dsi`, `allwinner,sun20i-d1-mipi-dsi`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `phys`, `phy-names`, `resets`, `port`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `vcc-dsi-supply`, `phys`, `phy-names`, `port`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (minItems=1); `clock-names` (declared by schema); `resets` (maxItems=1); `phys` (maxItems=1); `phy-names` (const `dphy`); `port` (ref `/schemas/graph.yaml#/properties/port`; The port should be the input endpoint, usually coming from the associated TCON.).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun6i-a31-mipi-dsi`, `allwinner,sun50i-a64-mipi-dsi`, `allwinner,sun50i-a100-mipi-dsi`, `allwinner,sun20i-d1-mipi-dsi`; provider bindings for `clocks`, `clock-names`, `resets`, `interrupts`, `phys`, `phy-names`, `port`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/port`, `dsi-controller.yaml#`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun6i-a31-mipi-dsi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (136 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun6i-a31-mipi-dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-de2-mixer.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-de2-mixer.yaml

## Purpose
Allwinner Display Engine 2.0 Mixer is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun8i-a83t-de2-mixer.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Allwinner Display Engine 2.0 Mixer.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun8i-a83t-de2-mixer.yaml#`, top-level `compatible` values `allwinner,sun8i-a83t-de2-mixer-0`, `allwinner,sun8i-a83t-de2-mixer-1`, `allwinner,sun8i-h3-de2-mixer-0`, `allwinner,sun8i-r40-de2-mixer-0`, `allwinner,sun8i-r40-de2-mixer-1`, `allwinner,sun8i-v3s-de2-mixer`, `allwinner,sun20i-d1-de2-mixer-0`, `allwinner,sun20i-d1-de2-mixer-1`, `allwinner,sun50i-a64-de2-mixer-0`, `allwinner,sun50i-a64-de2-mixer-1`, `allwinner,sun50i-h6-de3-mixer-0`, `allwinner,sun50i-h616-de33-mixer-0`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `ports`, and top-level properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `iommus`, `resets`, `ports`.
Key property contracts include: `compatible` (enum `allwinner,sun8i-a83t-de2-mixer-0`, `allwinner,sun8i-a83t-de2-mixer-1`, `allwinner,sun8i-h3-de2-mixer-0`, `allwinner,sun8i-r40-de2-mixer-0`, `allwinner,sun8i-r40-de2-mixer-1`, `allwinner,sun8i-v3s-de2-mixer`, `allwinner,sun20i-d1-de2-mixer-0`, `allwinner,sun20i-d1-de2-mixer-1`, and 4 more); `reg` (declared by schema); `clocks` (declared by schema); `clock-names` (declared by schema); `resets` (maxItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun8i-a83t-de2-mixer-0`, `allwinner,sun8i-a83t-de2-mixer-1`, `allwinner,sun8i-h3-de2-mixer-0`, `allwinner,sun8i-r40-de2-mixer-0`, and 8 more; provider bindings for `clocks`, `clock-names`, `resets`, `iommus`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-de2-mixer.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (140 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-de2-mixer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-dw-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-dw-hdmi.yaml

## Purpose
Allwinner A83t DWC HDMI TX Encoder is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun8i-a83t-dw-hdmi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The HDMI transmitter is a Synopsys DesignWare HDMI 1.4 TX controller IP with Allwinner\'s own PHY IP. It supports audio and video outputs and CEC. These DT bindings follow the Synopsys DWC HDMI TX bindings defined in bridge/synopsys,dw-hdmi.yaml with the following device-specific properties.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun8i-a83t-dw-hdmi.yaml#`, top-level `compatible` values `allwinner,sun8i-a83t-dw-hdmi`, `allwinner,sun50i-h6-dw-hdmi`, `allwinner,sun8i-h3-dw-hdmi`, `allwinner,sun8i-r40-dw-hdmi`, `allwinner,sun50i-a64-dw-hdmi`, required properties `compatible`, `reg`, `reg-io-width`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, `ports`, and top-level properties `#phy-cells`, `compatible`, `reg`, `reg-io-width`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, `hvcc-supply`, `ports`.
Key property contracts include: `#phy-cells` (const `0`); `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (minItems=3); `clock-names` (minItems=3); `resets` (minItems=1); `reset-names` (minItems=1); `phys` (maxItems=1; Phandle to the DWC HDMI PHY.); `phy-names` (const `phy`); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun8i-a83t-dw-hdmi`, `allwinner,sun50i-h6-dw-hdmi`, `allwinner,sun8i-h3-dw-hdmi`, `allwinner,sun8i-r40-dw-hdmi`, and 1 more; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `phys`, `phy-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-dw-hdmi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 2 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (253 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-dw-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-hdmi-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-hdmi-phy.yaml

## Purpose
Allwinner A83t HDMI PHY is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun8i-a83t-hdmi-phy.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Allwinner A83t HDMI PHY.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun8i-a83t-hdmi-phy.yaml#`, top-level `compatible` values `allwinner,sun8i-a83t-hdmi-phy`, `allwinner,sun8i-h3-hdmi-phy`, `allwinner,sun8i-r40-hdmi-phy`, `allwinner,sun50i-a64-hdmi-phy`, `allwinner,sun50i-h6-hdmi-phy`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, and top-level properties `#phy-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`.
Key property contracts include: `#phy-cells` (const `0`); `compatible` (enum `allwinner,sun8i-a83t-hdmi-phy`, `allwinner,sun8i-h3-hdmi-phy`, `allwinner,sun8i-r40-hdmi-phy`, `allwinner,sun50i-a64-hdmi-phy`, `allwinner,sun50i-h6-hdmi-phy`); `reg` (maxItems=1); `clocks` (minItems=2); `clock-names` (minItems=2); `resets` (maxItems=1); `reset-names` (const `phy`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun8i-a83t-hdmi-phy`, `allwinner,sun8i-h3-hdmi-phy`, `allwinner,sun8i-r40-hdmi-phy`, `allwinner,sun50i-a64-hdmi-phy`, and 1 more; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-hdmi-phy.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (115 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-a83t-hdmi-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-r40-tcon-top.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-r40-tcon-top.yaml

## Purpose
Allwinner R40 TCON TOP is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun8i-r40-tcon-top.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. TCON TOPs main purpose is to configure whole display pipeline. It determines relationships between mixers and TCONs, selects source TCON for HDMI, muxes LCD and TV encoder GPIO output, selects TV encoder clock source and contains additional TV TCON and DSI gates. It allows display pipeline to be configured in very d...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun8i-r40-tcon-top.yaml#`, top-level `compatible` values `allwinner,sun8i-r40-tcon-top`, `allwinner,sun20i-d1-tcon-top`, `allwinner,sun50i-h6-tcon-top`, required properties `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `clock-output-names`, `resets`, `ports`, and top-level properties `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `clock-output-names`, `resets`, `ports`.
Key property contracts include: `#clock-cells` (const `1`); `compatible` (enum `allwinner,sun8i-r40-tcon-top`, `allwinner,sun20i-d1-tcon-top`, `allwinner,sun50i-h6-tcon-top`); `reg` (maxItems=1); `clocks` (maxItems=6; minItems=2); `clock-names` (maxItems=6; minItems=2); `resets` (maxItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun8i-r40-tcon-top`, `allwinner,sun20i-d1-tcon-top`, `allwinner,sun50i-h6-tcon-top`; provider bindings for `clocks`, `clock-names`, `resets`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun8i-r40-tcon-top.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (329 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun8i-r40-tcon-top.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun9i-a80-deu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun9i-a80-deu.yaml

## Purpose
Allwinner A80 Detail Enhancement Unit is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `allwinner,sun9i-a80-deu.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The DEU (Detail Enhancement Unit), found in the Allwinner A80 SoC, can sharpen the display content in both luma and chroma channels.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/allwinner,sun9i-a80-deu.yaml#`, top-level `compatible` values `allwinner,sun9i-a80-deu`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `ports`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `ports`.
Key property contracts include: `compatible` (const `allwinner,sun9i-a80-deu`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `resets` (maxItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `allwinner,sun9i-a80-deu`; provider bindings for `clocks`, `clock-names`, `resets`, `interrupts`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/allwinner,sun9i-a80-deu.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (120 lines). Maintainers listed by the binding: `Chen-Yu Tsai <wens@csie.org>`, `Maxime Ripard <mripard@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/allwinner,sun9i-a80-deu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-dw-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-dw-hdmi.yaml

## Purpose
Amlogic specific extensions to the Synopsys Designware HDMI Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `amlogic,meson-dw-hdmi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Amlogic Meson Synopsys Designware Integration is composed of - A Synopsys DesignWare HDMI Controller IP - A TOP control block controlling the Clocks and PHY - A custom HDMI PHY in order to convert video to TMDS signal ___________________________________ | HDMI TOP |<= HPD |___________________________________| |...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/amlogic,meson-dw-hdmi.yaml#`, top-level `compatible` values `amlogic,meson-gxbb-dw-hdmi`, `amlogic,meson-gxl-dw-hdmi`, `amlogic,meson-gxm-dw-hdmi`, `amlogic,meson-gx-dw-hdmi`, `amlogic,meson-g12a-dw-hdmi`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `port@0`, `port@1`, `#address-cells`, `#size-cells`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `hdmi-supply`, `port@0`, `port@1`, `#address-cells`, `#size-cells`, `#sound-dai-cells`, `sound-name-prefix`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (minItems=3); `clock-names` (declared by schema); `power-domains` (maxItems=1; phandle to the associated power domain); `resets` (minItems=3); `reset-names` (declared by schema); `#address-cells` (const `1`); `#size-cells` (const `0`); `#sound-dai-cells` (const `0`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `amlogic,meson-gxbb-dw-hdmi`, `amlogic,meson-gxl-dw-hdmi`, `amlogic,meson-gxm-dw-hdmi`, `amlogic,meson-gx-dw-hdmi`, and 1 more; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `power-domains`.
Referenced shared schemas include `/schemas/sound/dai-common.yaml#`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/amlogic,meson-dw-hdmi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (157 lines). Maintainers listed by the binding: `Neil Armstrong <neil.armstrong@linaro.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-dw-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-g12a-dw-mipi-dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-g12a-dw-mipi-dsi.yaml

## Purpose
Amlogic specific extensions to the Synopsys Designware MIPI DSI Host Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `amlogic,meson-g12a-dw-mipi-dsi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Amlogic Meson Synopsys Designware Integration is composed of - A Synopsys DesignWare MIPI DSI Host Controller IP - A TOP control block controlling the Clocks & Resets of the IP

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/amlogic,meson-g12a-dw-mipi-dsi.yaml#`, top-level `compatible` values `amlogic,meson-g12a-dw-mipi-dsi`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, `ports`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, `ports`.
Key property contracts include: `compatible` (enum `amlogic,meson-g12a-dw-mipi-dsi`); `reg` (maxItems=1); `clocks` (maxItems=4; minItems=3); `clock-names` (minItems=3); `resets` (maxItems=1); `reset-names` (declared by schema); `phys` (maxItems=1); `phy-names` (declared by schema); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `amlogic,meson-g12a-dw-mipi-dsi`; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, `ports`.
Referenced shared schemas include `dsi-controller.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/amlogic,meson-g12a-dw-mipi-dsi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (118 lines). Maintainers listed by the binding: `Neil Armstrong <neil.armstrong@linaro.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-g12a-dw-mipi-dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-vpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-vpu.yaml

## Purpose
Amlogic Meson Display Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `amlogic,meson-vpu.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Amlogic Meson Display controller is composed of several components that are going to be documented below DMC|---------------VPU (Video Processing Unit)----------------|------HHI------| | vd1 _______ _____________ _________________ | | D |-------| |----| | | | | HDMI PLL | D | vd2 | VIU | | Video Post | | Video E...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/amlogic,meson-vpu.yaml#`, top-level `compatible` values `amlogic,meson-gxbb-vpu`, `amlogic,meson-gxl-vpu`, `amlogic,meson-gxm-vpu`, `amlogic,meson-gx-vpu`, `amlogic,meson-g12a-vpu`, required properties `compatible`, `reg`, `interrupts`, `port@0`, `port@1`, `#address-cells`, `#size-cells`, `amlogic,canvas`, and top-level properties `compatible`, `reg`, `reg-names`, `interrupts`, `amlogic,canvas`, `power-domains`, `port@0`, `port@1`, `port@2`, `#address-cells`, `#size-cells`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=2); `interrupts` (maxItems=1); `amlogic,canvas` (ref `/schemas/types.yaml#/definitions/phandle`; should point to a canvas provider node); `power-domains` (maxItems=1; phandle to the associated power domain); `#address-cells` (const `1`); `#size-cells` (const `0`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `amlogic,meson-gxbb-vpu`, `amlogic,meson-gxl-vpu`, `amlogic,meson-gxm-vpu`, `amlogic,meson-gx-vpu`, and 1 more; provider bindings for `interrupts`, `power-domains`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/amlogic,meson-vpu.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (149 lines). Maintainers listed by the binding: `Neil Armstrong <neil.armstrong@linaro.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/amlogic,meson-vpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/apple,h7-display-pipe-mipi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/apple,h7-display-pipe-mipi.yaml

## Purpose
Apple pre-DCP display controller MIPI interface is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `apple,h7-display-pipe-mipi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The MIPI controller part of the pre-DCP Apple display controller

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/apple,h7-display-pipe-mipi.yaml#`, top-level `compatible` values `apple,t8112-display-pipe-mipi`, `apple,t8103-display-pipe-mipi`, `apple,h7-display-pipe-mipi`, required properties `compatible`, `reg`, `ports`, and top-level properties `compatible`, `reg`, `power-domains`, `ports`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `power-domains` (maxItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `apple,t8112-display-pipe-mipi`, `apple,t8103-display-pipe-mipi`, `apple,h7-display-pipe-mipi`; provider bindings for `power-domains`, `ports`.
Referenced shared schemas include `dsi-controller.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/apple,h7-display-pipe-mipi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (83 lines). Maintainers listed by the binding: `Sasha Finkelstein <k@chaosmail.tech>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/apple,h7-display-pipe-mipi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/apple,h7-display-pipe.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/apple,h7-display-pipe.yaml

## Purpose
Apple pre-DCP display controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `apple,h7-display-pipe.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. A secondary display controller used to drive the "touchbar" on certain Apple laptops.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/apple,h7-display-pipe.yaml#`, top-level `compatible` values `apple,t8112-display-pipe`, `apple,t8103-display-pipe`, `apple,h7-display-pipe`, required properties `compatible`, `reg`, `interrupts`, `port`, and top-level properties `compatible`, `reg`, `reg-names`, `power-domains`, `interrupts`, `interrupt-names`, `iommus`, `port`.
Key property contracts include: `compatible` (declared by schema); `reg` (declared by schema); `power-domains` (maxItems=2; Phandles to pmgr entries that are needed for this controller to turn on. Aside from that, their specific functions are unknown); `interrupts` (declared by schema); `interrupt-names` (declared by schema); `port` (ref `/schemas/graph.yaml#/properties/port`; Output port. Always connected to apple,h7-display-pipe-mipi).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `apple,t8112-display-pipe`, `apple,t8103-display-pipe`, `apple,h7-display-pipe`; provider bindings for `interrupts`, `interrupt-names`, `iommus`, `power-domains`, `port`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/apple,h7-display-pipe.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (88 lines). Maintainers listed by the binding: `Sasha Finkelstein <k@chaosmail.tech>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/apple,h7-display-pipe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,hdlcd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,hdlcd.yaml

## Purpose
Arm HDLCD display controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `arm,hdlcd.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Arm HDLCD is a display controller found on several development platforms produced by ARM Ltd and in more modern of its Fast Models. The HDLCD is an RGB streamer that reads the data from a framebuffer and sends it to a single digital encoder (DVI or HDMI).

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/arm,hdlcd.yaml#`, top-level `compatible` values `arm,hdlcd`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `port`, and top-level properties `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `memory-region`, `iommus`, `port`.
Key property contracts include: `compatible` (const `arm,hdlcd`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clock-names` (const `pxlclk`); `clocks` (maxItems=1; The input reference for the pixel clock.); `port` (ref `/schemas/graph.yaml#/properties/port`; Output endpoint of the controller, connecting the LCD panel signals.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `arm,hdlcd`; provider bindings for `clocks`, `clock-names`, `interrupts`, `iommus`, `port`, `memory-region`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/arm,hdlcd.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (89 lines). Maintainers listed by the binding: `Liviu Dudau <Liviu.Dudau@arm.com>`, `Andre Przywara <andre.przywara@arm.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,hdlcd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,komeda.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,komeda.yaml

## Purpose
Arm Komeda display processor is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `arm,komeda.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Arm Mali D71 display processor supports up to two displays with up to a 4K resolution each. Each pipeline can be composed of up to four layers. It is typically connected to a digital display connector like HDMI.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/arm,komeda.yaml#`, top-level `compatible` values `arm,mali-d32`, `armchina,linlon-d6`, `arm,mali-d71`, required properties `#address-cells`, `#size-cells`, `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `pipeline@0`, and top-level properties `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `#address-cells`, `#size-cells`, `memory-region`, `iommus`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `interrupts` (maxItems=1); `clock-names` (const `aclk`); `clocks` (maxItems=1; The main DPU processor clock); `#address-cells` (const `1`); `#size-cells` (const `0`).
The schema also defines pattern properties `^pipeline@[01]$`, which describe child nodes or reusable node fragments.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `arm,mali-d32`, `armchina,linlon-d6`, `arm,mali-d71`; provider bindings for `clocks`, `clock-names`, `interrupts`, `iommus`, `memory-region`.
Referenced shared schemas include `/schemas/graph.yaml#/$defs/port-base`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/arm,komeda.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (133 lines). Maintainers listed by the binding: `Liviu Dudau <Liviu.Dudau@arm.com>`, `Andre Przywara <andre.przywara@arm.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,komeda.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,malidp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,malidp.yaml

## Purpose
Arm Mali Display Processor (Mali-DP) is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `arm,malidp.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The following bindings apply to a family of Display Processors sold as licensable IP by ARM Ltd. The bindings describe the Mali DP500, DP550 and DP650 processors that offer multiple composition layers, support for rotation and scaling output.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/arm,malidp.yaml#`, top-level `compatible` values `arm,mali-dp500`, `arm,mali-dp550`, `arm,mali-dp650`, required properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `port`, `arm,malidp-output-port-lines`, and top-level properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clock-names`, `clocks`, `memory-region`, `arm,malidp-output-port-lines`, `arm,malidp-arqos-value`, `port`.
Key property contracts include: `compatible` (enum `arm,mali-dp500`, `arm,mali-dp550`, `arm,mali-dp650`); `reg` (maxItems=1); `interrupts` (declared by schema); `interrupt-names` (declared by schema); `clock-names` (declared by schema); `clocks` (declared by schema); `arm,malidp-output-port-lines` (ref `/schemas/types.yaml#/definitions/uint8-array`; Number of output lines/bits for each colour channel.); `arm,malidp-arqos-value` (ref `/schemas/types.yaml#/definitions/uint32`; Quality-of-Service value for the display engine FIFOs, to write into the RQOS register of the DP500. See the ARM Mali-DP500 TRM for details on the encoding. If omitted, the RQOS register will not be changed.); `port` (ref `/schemas/graph.yaml#/properties/port`; Output endpoint of the controller, connecting the LCD panel signals.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `arm,mali-dp500`, `arm,mali-dp550`, `arm,mali-dp650`; provider bindings for `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `port`, `memory-region`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/arm,malidp.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (119 lines). Maintainers listed by the binding: `Liviu Dudau <Liviu.Dudau@arm.com>`, `Andre Przywara <andre.przywara@arm.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,malidp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,pl11x.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,pl11x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel,lcdc-display.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel,lcdc-display.yaml

## Purpose
Microchip's LCDC Display is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `atmel,lcdc-display.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The LCD Controller (LCDC) consists of logic for transferring LCD image data from an external display buffer to a TFT LCD panel. The LCDC has one display input buffer per layer that fetches pixels through the single bus host interface and a look-up table to allow palletized display configurations. The LCDC is program...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/atmel,lcdc-display.yaml#`, top-level `compatible` values none declared, required properties `atmel,dmacon`, `atmel,lcdcon2`, `atmel,guard-time`, `bits-per-pixel`, and top-level properties `atmel,dmacon`, `atmel,lcdcon2`, `atmel,guard-time`, `bits-per-pixel`, `atmel,lcdcon-backlight`, `atmel,lcdcon-backlight-inverted`, `atmel,lcd-wiring-mode`, `atmel,power-control-gpio`, `display-timings`.
Key property contracts include: `atmel,dmacon` (ref `/schemas/types.yaml#/definitions/uint32`; dma controller configuration); `atmel,lcdcon2` (ref `/schemas/types.yaml#/definitions/uint32`; lcd controller configuration); `atmel,guard-time` (ref `/schemas/types.yaml#/definitions/uint32`; lcd guard time (Delay in frame periods)); `atmel,lcdcon-backlight` (ref `/schemas/types.yaml#/definitions/flag`; enable backlight); `atmel,lcdcon-backlight-inverted` (ref `/schemas/types.yaml#/definitions/flag`; invert backlight PWM polarity); `atmel,lcd-wiring-mode` (enum `RGB`, `BRG`; ref `/schemas/types.yaml#/definitions/string`; lcd wiring mode "RGB" or "BRG"); `atmel,power-control-gpio` (maxItems=1; gpio to power on or off the LCD (as many as needed)).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `panel/display-timings.yaml#`.

## Risks
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/atmel,lcdc-display.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (103 lines). Maintainers listed by the binding: `Nicolas Ferre <nicolas.ferre@microchip.com>`, `Dharma Balasubiramani <dharma.b@microchip.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel,lcdc-display.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel,lcdc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel,lcdc.yaml

## Purpose
Microchip's LCDC Framebuffer is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `atmel,lcdc.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The LCDC works with a framebuffer, which is a section of memory that contains a complete frame of data representing pixel values for the display. The LCDC reads the pixel data from the framebuffer and sends it to the LCD panel to render the image.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/atmel,lcdc.yaml#`, top-level `compatible` values `atmel,at91sam9261-lcdc`, `atmel,at91sam9263-lcdc`, `atmel,at91sam9g10-lcdc`, `atmel,at91sam9g45-lcdc`, `atmel,at91sam9g45es-lcdc`, `atmel,at91sam9rl-lcdc`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `display`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `display`.
Key property contracts include: `compatible` (enum `atmel,at91sam9261-lcdc`, `atmel,at91sam9263-lcdc`, `atmel,at91sam9g10-lcdc`, `atmel,at91sam9g45-lcdc`, `atmel,at91sam9g45es-lcdc`, `atmel,at91sam9rl-lcdc`); `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (maxItems=2); `clock-names` (declared by schema).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `atmel,at91sam9261-lcdc`, `atmel,at91sam9263-lcdc`, `atmel,at91sam9g10-lcdc`, `atmel,at91sam9g45-lcdc`, and 2 more; provider bindings for `clocks`, `clock-names`, `interrupts`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/atmel,lcdc.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (70 lines). Maintainers listed by the binding: `Nicolas Ferre <nicolas.ferre@microchip.com>`, `Dharma Balasubiramani <dharma.b@microchip.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel,lcdc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel/atmel,hlcdc-display-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel/atmel,hlcdc-display-controller.yaml

## Purpose
Atmel's High LCD Controller (HLCDC) is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `atmel,hlcdc-display-controller.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The LCD Controller (LCDC) consists of logic for transferring LCD image data from an external display buffer to a TFT LCD panel. The LCDC has one display input buffer per layer that fetches pixels through the single bus host interface and a look-up table to allow palletized display configurations.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/atmel/atmel,hlcdc-display-controller.yaml#`, top-level `compatible` values `atmel,hlcdc-display-controller`, required properties `#address-cells`, `#size-cells`, `compatible`, `port@0`, and top-level properties `compatible`, `#address-cells`, `#size-cells`, `port@0`.
Key property contracts include: `compatible` (const `atmel,hlcdc-display-controller`); `#address-cells` (const `1`); `#size-cells` (const `0`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `atmel,hlcdc-display-controller`.
Referenced shared schemas include `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/atmel/atmel,hlcdc-display-controller.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- add or update example nodes when changing required resources so validation covers the intended binding shape

## Source Notes
The source was read in full for this research pass (63 lines). Maintainers listed by the binding: `Nicolas Ferre <nicolas.ferre@microchip.com>`, `Alexandre Belloni <alexandre.belloni@bootlin.com>`, `Claudiu Beznea <claudiu.beznea@tuxon.dev>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/atmel/atmel,hlcdc-display-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2711-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2711-hdmi.yaml

## Purpose
Broadcom BCM2711 HDMI Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2711-hdmi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom BCM2711 HDMI Controller.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2711-hdmi.yaml#`, top-level `compatible` values `brcm,bcm2711-hdmi0`, `brcm,bcm2711-hdmi1`, `brcm,bcm2712-hdmi0`, `brcm,bcm2712-hdmi1`, required properties `compatible`, `reg`, `reg-names`, `clocks`, `resets`, `ddc`, and top-level properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `ddc`, `hpd-gpios`, `dmas`, `dma-names`, `resets`, `wifi-2.4ghz-coexistence`.
Key property contracts include: `compatible` (enum `brcm,bcm2711-hdmi0`, `brcm,bcm2711-hdmi1`, `brcm,bcm2712-hdmi0`, `brcm,bcm2712-hdmi1`); `reg` (declared by schema); `clocks` (declared by schema); `clock-names` (declared by schema); `interrupts` (maxItems=6; minItems=5); `interrupt-names` (maxItems=6; minItems=5); `dmas` (maxItems=1; Should contain one entry pointing to the DMA channel used to transfer audio data.); `dma-names` (const `audio-rx`); `resets` (maxItems=1).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2711-hdmi0`, `brcm,bcm2711-hdmi1`, `brcm,bcm2712-hdmi0`, `brcm,bcm2712-hdmi1`; provider bindings for `clocks`, `clock-names`, `resets`, `interrupts`, `interrupt-names`, `dmas`, `dma-names`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2711-hdmi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (191 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2711-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-dpi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-dpi.yaml

## Purpose
Broadcom VC4 (VideoCore4) DPI Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-dpi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom VC4 (VideoCore4) DPI Controller.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-dpi.yaml#`, top-level `compatible` values `brcm,bcm2835-dpi`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `port`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `port`.
Key property contracts include: `compatible` (const `brcm,bcm2835-dpi`); `reg` (maxItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `port` (ref `/schemas/graph.yaml#/properties/port`; Port node with a single endpoint connecting to the panel.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2835-dpi`; provider bindings for `clocks`, `clock-names`, `port`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-dpi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (61 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-dpi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-dsi0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-dsi0.yaml

## Purpose
Broadcom VC4 (VideoCore4) DSI Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-dsi0.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom VC4 (VideoCore4) DSI Controller.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-dsi0.yaml#`, top-level `compatible` values `brcm,bcm2711-dsi1`, `brcm,bcm2835-dsi0`, `brcm,bcm2835-dsi1`, required properties `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `clock-output-names`, `interrupts`, and top-level properties `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `clock-output-names`, `interrupts`, `power-domains`.
Key property contracts include: `#clock-cells` (const `1`); `compatible` (enum `brcm,bcm2711-dsi1`, `brcm,bcm2835-dsi0`, `brcm,bcm2835-dsi1`); `reg` (maxItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `interrupts` (maxItems=1); `power-domains` (maxItems=1).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2711-dsi1`, `brcm,bcm2835-dsi0`, `brcm,bcm2835-dsi1`; provider bindings for `clocks`, `clock-names`, `interrupts`, `power-domains`.
Referenced shared schemas include `dsi-controller.yaml#`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-dsi0.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (85 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-dsi0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-hdmi.yaml

## Purpose
Broadcom VC4 (VideoCore4) HDMI Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-hdmi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom VC4 (VideoCore4) HDMI Controller.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-hdmi.yaml#`, top-level `compatible` values `brcm,bcm2835-hdmi`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `ddc`, and top-level properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `ddc`, `hpd-gpios`, `dmas`, `dma-names`, `power-domains`.
Key property contracts include: `compatible` (const `brcm,bcm2835-hdmi`); `reg` (declared by schema); `interrupts` (minItems=2); `clocks` (declared by schema); `clock-names` (declared by schema); `dmas` (maxItems=1; Should contain one entry pointing to the DMA channel used to transfer audio data.); `dma-names` (const `audio-rx`); `power-domains` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2835-hdmi`; provider bindings for `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`, `power-domains`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-hdmi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (83 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-hvs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-hvs.yaml

## Purpose
Broadcom VC4 (VideoCore4) Hardware Video Scaler is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-hvs.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom VC4 (VideoCore4) Hardware Video Scaler.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-hvs.yaml#`, top-level `compatible` values `brcm,bcm2711-hvs`, `brcm,bcm2712-hvs`, `brcm,bcm2835-hvs`, required properties `compatible`, `reg`, `interrupts`, and top-level properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`.
Key property contracts include: `compatible` (enum `brcm,bcm2711-hvs`, `brcm,bcm2712-hvs`, `brcm,bcm2835-hvs`); `reg` (maxItems=1); `interrupts` (maxItems=3; minItems=1); `interrupt-names` (maxItems=3; minItems=1); `clocks` (maxItems=2; minItems=1); `clock-names` (maxItems=2; minItems=1).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2711-hvs`, `brcm,bcm2712-hvs`, `brcm,bcm2835-hvs`; provider bindings for `clocks`, `clock-names`, `interrupts`, `interrupt-names`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-hvs.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (116 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-hvs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-pixelvalve0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-pixelvalve0.yaml

## Purpose
Broadcom VC4 (VideoCore4) PixelValve is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-pixelvalve0.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom VC4 (VideoCore4) PixelValve.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-pixelvalve0.yaml#`, top-level `compatible` values `brcm,bcm2835-pixelvalve0`, `brcm,bcm2835-pixelvalve1`, `brcm,bcm2835-pixelvalve2`, `brcm,bcm2711-pixelvalve0`, `brcm,bcm2711-pixelvalve1`, `brcm,bcm2711-pixelvalve2`, `brcm,bcm2711-pixelvalve3`, `brcm,bcm2711-pixelvalve4`, `brcm,bcm2712-pixelvalve0`, `brcm,bcm2712-pixelvalve1`, `brcm,bcm2712-pixelvalve2`, required properties `compatible`, `reg`, `interrupts`, and top-level properties `compatible`, `reg`, `interrupts`.
Key property contracts include: `compatible` (enum `brcm,bcm2835-pixelvalve0`, `brcm,bcm2835-pixelvalve1`, `brcm,bcm2835-pixelvalve2`, `brcm,bcm2711-pixelvalve0`, `brcm,bcm2711-pixelvalve1`, `brcm,bcm2711-pixelvalve2`, `brcm,bcm2711-pixelvalve3`, `brcm,bcm2711-pixelvalve4`, and 3 more); `reg` (maxItems=1); `interrupts` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2835-pixelvalve0`, `brcm,bcm2835-pixelvalve1`, `brcm,bcm2835-pixelvalve2`, `brcm,bcm2711-pixelvalve0`, and 7 more; provider bindings for `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-pixelvalve0.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (48 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-pixelvalve0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-txp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-txp.yaml

## Purpose
Broadcom VC4 (VideoCore4) TXP (writeback) Controller is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-txp.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom VC4 (VideoCore4) TXP (writeback) Controller.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-txp.yaml#`, top-level `compatible` values `brcm,bcm2712-mop`, `brcm,bcm2712-moplet`, `brcm,bcm2835-txp`, required properties `compatible`, `reg`, `interrupts`, and top-level properties `compatible`, `reg`, `interrupts`.
Key property contracts include: `compatible` (enum `brcm,bcm2712-mop`, `brcm,bcm2712-moplet`, `brcm,bcm2835-txp`); `reg` (maxItems=1); `interrupts` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2712-mop`, `brcm,bcm2712-moplet`, `brcm,bcm2835-txp`; provider bindings for `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-txp.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (40 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-txp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-v3d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-v3d.yaml

## Purpose
Broadcom VC4 (VideoCore4) V3D GPU is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-v3d.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Broadcom VC4 (VideoCore4) V3D GPU.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-v3d.yaml#`, top-level `compatible` values `brcm,bcm2835-v3d`, `brcm,cygnus-v3d`, required properties `compatible`, `reg`, `interrupts`, and top-level properties `compatible`, `reg`, `clocks`, `interrupts`, `power-domains`.
Key property contracts include: `compatible` (enum `brcm,bcm2835-v3d`, `brcm,cygnus-v3d`); `reg` (maxItems=1); `clocks` (maxItems=1); `interrupts` (maxItems=1); `power-domains` (maxItems=1).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2835-v3d`, `brcm,cygnus-v3d`; provider bindings for `clocks`, `interrupts`, `power-domains`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-v3d.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (45 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-v3d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-vc4.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-vc4.yaml

## Purpose
Broadcom VC4 (VideoCore4) GPU is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `brcm,bcm2835-vc4.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The VC4 device present on the Raspberry Pi includes a display system with HDMI output and the HVS (Hardware Video Scaler) for compositing display planes.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/brcm,bcm2835-vc4.yaml#`, top-level `compatible` values `brcm,bcm2711-vc5`, `brcm,bcm2712-vc6`, `brcm,bcm2835-vc4`, `brcm,cygnus-vc4`, required properties `compatible`, and top-level properties `compatible`.
Key property contracts include: `compatible` (enum `brcm,bcm2711-vc5`, `brcm,bcm2712-vc6`, `brcm,bcm2835-vc4`, `brcm,cygnus-vc4`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `brcm,bcm2711-vc5`, `brcm,bcm2712-vc6`, `brcm,bcm2835-vc4`, `brcm,cygnus-vc4`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/brcm,bcm2835-vc4.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (36 lines). Maintainers listed by the binding: `Eric Anholt <eric@anholt.net>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-vc4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-vec.yaml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/brcm,bcm2835-vec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/adi,adv7511.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/adi,adv7511.yaml

## Purpose
Analog Devices ADV7511/11W/13 HDMI Encoders is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `adi,adv7511.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The ADV7511, ADV7511W and ADV7513 are HDMI audio and video transmitters compatible with HDMI 1.4 and DVI 1.0. They support color space conversion, S/PDIF, CEC and HDCP. The transmitter input is parallel RGB or YUV data.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/adi,adv7511.yaml#`, top-level `compatible` values `adi,adv7511`, `adi,adv7511w`, `adi,adv7513`, required properties `compatible`, `reg`, `ports`, `adi,input-depth`, `adi,input-colorspace`, `adi,input-clock`, `avdd-supply`, `dvdd-supply`, `pvdd-supply`, `dvdd-3v-supply`, `bgvdd-supply`, and top-level properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `pd-gpios`, `avdd-supply`, `dvdd-supply`, `pvdd-supply`, `dvdd-3v-supply`, `bgvdd-supply`, `adi,input-depth`, `adi,input-colorspace`, `adi,input-clock`, `adi,clock-delay`, `adi,embedded-sync`, `adi,input-style`, and 2 more.
Key property contracts include: `compatible` (enum `adi,adv7511`, `adi,adv7511w`, `adi,adv7513`); `reg` (maxItems=4; minItems=1; I2C slave addresses. The ADV7511/11W/13 internal registers are split into four pages exposed through different I2C addresses, creating four register maps. Each map has it own I2C address and acts as a standard slave device on the I2C bus. The main address is mandatory, others are optional and revert to defaults if n...); `clocks` (maxItems=1; Reference to the CEC clock.); `clock-names` (const `cec`); `interrupts` (maxItems=1); `adi,input-depth` (enum `8`, `10`, `12`; ref `/schemas/types.yaml#/definitions/uint32`; Number of bits per color component at the input.); `adi,input-colorspace` (enum `rgb`, `yuv422`, `yuv444`; Input color space.); `adi,input-clock` (enum `1x`, `2x`, `dd`; Input clock type. "1x": one clock cycle per pixel "2x": two clock cycles per pixel "dd": one clock cycle per pixel, data driven on both edges); `adi,clock-delay` (ref `/schemas/types.yaml#/definitions/uint32`; Video data clock delay relative to the pixel clock, in ps (-1200ps .. 1600 ps).); `adi,embedded-sync` (If defined, the input uses synchronization signals embedded in the data stream (similar to BT.656).); `adi,input-style` (enum `1`, `2`, `3`; ref `/schemas/types.yaml#/definitions/uint32`; Input components arrangement variant as listed in the input format tables in the datasheet.); `adi,input-justification` (enum `left`, `evenly`, `right`; Input bit justification.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `adi,adv7511`, `adi,adv7511w`, `adi,adv7513`; provider bindings for `clocks`, `clock-names`, `interrupts`, `ports`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/adi,adv7511.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (236 lines). Maintainers listed by the binding: `Laurent Pinchart <laurent.pinchart@ideasonboard.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/adi,adv7511.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/adi,adv7533.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/adi,adv7533.yaml

## Purpose
Analog Devices ADV7533/35 HDMI Encoders is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `adi,adv7533.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The ADV7533 and ADV7535 are HDMI audio and video transmitters compatible with HDMI 1.4 and DVI 1.0. They support color space conversion, S/PDIF, CEC and HDCP. The transmitter input is MIPI DSI.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/adi,adv7533.yaml#`, top-level `compatible` values `adi,adv7533`, `adi,adv7535`, required properties `compatible`, `reg`, `ports`, `adi,dsi-lanes`, `avdd-supply`, `dvdd-supply`, `pvdd-supply`, `a2vdd-supply`, `v3p3-supply`, and top-level properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `pd-gpios`, `avdd-supply`, `dvdd-supply`, `pvdd-supply`, `a2vdd-supply`, `v3p3-supply`, `v1p2-supply`, `adi,disable-timing-generator`, `adi,dsi-lanes`, `#sound-dai-cells`, `ports`.
Key property contracts include: `compatible` (enum `adi,adv7533`, `adi,adv7535`); `reg` (maxItems=4; minItems=1; I2C slave addresses. The ADV7533/35 internal registers are split into four pages exposed through different I2C addresses, creating four register maps. Each map has it own I2C address and acts as a standard slave device on the I2C bus. The main address is mandatory, others are optional and revert to defaults if not s...); `clocks` (maxItems=1; Reference to the CEC clock.); `clock-names` (const `cec`); `interrupts` (maxItems=1); `adi,disable-timing-generator` (Disables the internal timing generator. The chip will rely on the sync signals in the DSI data lanes, rather than generating its own timings for HDMI output.); `adi,dsi-lanes` (enum `2`, `3`, `4`; ref `/schemas/types.yaml#/definitions/uint32`; Number of DSI data lanes connected to the DSI host.); `#sound-dai-cells` (const `0`); `ports` (ref `/schemas/graph.yaml#/properties/ports`; The ADV7533/35 has two video ports and one audio port.).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `adi,adv7533`, `adi,adv7535`; provider bindings for `clocks`, `clock-names`, `interrupts`, `ports`.
Referenced shared schemas include `/schemas/sound/dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/adi,adv7533.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (188 lines). Maintainers listed by the binding: `Laurent Pinchart <laurent.pinchart@ideasonboard.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/adi,adv7533.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,anx7625.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,anx7625.yaml

## Purpose
Analogix ANX7625 SlimPort (4K Mobile HD Transmitter) is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `analogix,anx7625.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The ANX7625 is an ultra-low power 4K Mobile HD Transmitter designed for portable devices.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/analogix,anx7625.yaml#`, top-level `compatible` values `analogix,anx7625`, required properties `compatible`, `reg`, `vdd10-supply`, `vdd18-supply`, `vdd33-supply`, `ports`, and top-level properties `compatible`, `reg`, `interrupts`, `enable-gpios`, `reset-gpios`, `vdd10-supply`, `vdd18-supply`, `vdd33-supply`, `analogix,lane0-swing`, `analogix,lane1-swing`, `analogix,audio-enable`, `aux-bus`, `connector`, `ports`.
Key property contracts include: `compatible` (const `analogix,anx7625`); `reg` (maxItems=1); `interrupts` (maxItems=1; used for interrupt pin B8.); `analogix,lane0-swing` (maxItems=20; minItems=1; ref `/schemas/types.yaml#/definitions/uint8-array`; an array of swing register setting for DP tx lane0 PHY. Registers 0~9 are Swing0_Pre0, Swing1_Pre0, Swing2_Pre0, Swing3_Pre0, Swing0_Pre1, Swing1_Pre1, Swing2_Pre1, Swing0_Pre2, Swing1_Pre2, Swing0_Pre3, they are for [Boost control] and [Swing control] setting. Registers 0~9, bit 3:0 is [Boost control], these bits c...); `analogix,lane1-swing` (maxItems=20; minItems=1; ref `/schemas/types.yaml#/definitions/uint8-array`; an array of swing register setting for DP tx lane1 PHY. DP TX lane1 swing register setting same with lane0 swing, please refer lane0-swing property description.); `analogix,audio-enable` (let the driver enable audio HDMI codec function or not.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `analogix,anx7625`; provider bindings for `interrupts`, `ports`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/display/dp-aux-bus.yaml#`, `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/analogix,anx7625.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 2 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (283 lines). Maintainers listed by the binding: `Xin Ji <xji@analogixsemi.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,anx7625.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,anx7814.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,anx7814.yaml

## Purpose
Analogix ANX7814 SlimPort (Full-HD Transmitter) is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `analogix,anx7814.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Analogix ANX7814 SlimPort (Full-HD Transmitter).

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/analogix,anx7814.yaml#`, top-level `compatible` values `analogix,anx7808`, `analogix,anx7812`, `analogix,anx7814`, `analogix,anx7816`, `analogix,anx7818`, required properties `compatible`, `reg`, `ports`, and top-level properties `compatible`, `reg`, `interrupts`, `hpd-gpios`, `pd-gpios`, `reset-gpios`, `dvdd10-supply`, `ports`.
Key property contracts include: `compatible` (enum `analogix,anx7808`, `analogix,anx7812`, `analogix,anx7814`, `analogix,anx7816`, `analogix,anx7818`); `reg` (maxItems=1; I2C address of the device.); `interrupts` (maxItems=1; Should contain the INTP interrupt.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `analogix,anx7808`, `analogix,anx7812`, `analogix,anx7814`, `analogix,anx7816`, and 1 more; provider bindings for `interrupts`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/analogix,anx7814.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (109 lines). Maintainers listed by the binding: `Andrzej Hajda <andrzej.hajda@intel.com>`, `Neil Armstrong <neil.armstrong@linaro.org>`, `Robert Foss <robert.foss@linaro.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,anx7814.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,dp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,dp.yaml

## Purpose
Analogix Display Port bridge is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `analogix,dp.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Analogix Display Port bridge.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/analogix,dp.yaml#`, top-level `compatible` values none declared, required properties `reg`, `interrupts`, `clock-names`, `clocks`, `ports`, and top-level properties `reg`, `interrupts`, `clocks`, `clock-names`, `phys`, `phy-names`, `force-hpd`, `hpd-gpios`, `ports`.
Key property contracts include: `reg` (maxItems=1); `interrupts` (maxItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `phys` (declared by schema); `phy-names` (const `dp`); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; provider bindings for `clocks`, `clock-names`, `interrupts`, `phys`, `phy-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/analogix,dp.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- add or update example nodes when changing required resources so validation covers the intended binding shape

## Source Notes
The source was read in full for this research pass (64 lines). Maintainers listed by the binding: `Rob Herring <robh@kernel.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/analogix,dp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/anx6345.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/anx6345.yaml

## Purpose
Analogix ANX6345 eDP Transmitter is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `anx6345.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The ANX6345 is an ultra-low power Full-HD eDP transmitter designed for portable devices.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/anx6345.yaml#`, top-level `compatible` values `analogix,anx6345`, required properties `compatible`, `reg`, `reset-gpios`, `dvdd12-supply`, `dvdd25-supply`, `ports`, and top-level properties `compatible`, `reg`, `reset-gpios`, `dvdd12-supply`, `dvdd25-supply`, `ports`.
Key property contracts include: `compatible` (const `analogix,anx6345`); `reg` (maxItems=1; base I2C address of the device); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `analogix,anx6345`; provider bindings for `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/anx6345.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (94 lines). Maintainers listed by the binding: `Torsten Duwe <duwe@lst.de>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/anx6345.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/cdns,dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/cdns,dsi.yaml

## Purpose
Cadence DSI bridge is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `cdns,dsi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. CDNS DSI is a bridge device which converts DPI to DSI

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/cdns,dsi.yaml#`, top-level `compatible` values `cdns,dsi`, `ti,j721e-dsi`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `phys`, `phy-names`, `ports`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `phys`, `phy-names`, `interrupts`, `resets`, `reset-names`, `ports`.
Key property contracts include: `compatible` (enum `cdns,dsi`, `ti,j721e-dsi`); `reg` (minItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `phys` (maxItems=1); `phy-names` (const `dphy`); `interrupts` (maxItems=1); `resets` (maxItems=1); `reset-names` (const `dsi_p_rst`); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `cdns,dsi`, `ti,j721e-dsi`; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `phys`, `phy-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`, `../dsi-controller.yaml#`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/cdns,dsi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 2 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (180 lines). Maintainers listed by the binding: `Boris Brezillon <boris.brezillon@bootlin.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/cdns,dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/cdns,mhdp8546.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/cdns,mhdp8546.yaml

## Purpose
Cadence MHDP8546 bridge is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `cdns,mhdp8546.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Cadence MHDP8546 bridge.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/cdns,mhdp8546.yaml#`, top-level `compatible` values `cdns,mhdp8546`, `ti,j721e-mhdp8546`, required properties `compatible`, `clocks`, `reg`, `reg-names`, `phys`, `phy-names`, `interrupts`, `ports`, and top-level properties `compatible`, `reg`, `reg-names`, `clocks`, `phys`, `phy-names`, `power-domains`, `interrupts`, `ports`.
Key property contracts include: `compatible` (enum `cdns,mhdp8546`, `ti,j721e-mhdp8546`); `reg` (minItems=1); `clocks` (maxItems=1; DP bridge clock, used by the IP to know how to translate a number of clock cycles into a time (which is used to comply with DP standard timings and delays).); `phys` (maxItems=1; phandle to the DisplayPort PHY.); `phy-names` (declared by schema); `power-domains` (maxItems=1); `interrupts` (maxItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `cdns,mhdp8546`, `ti,j721e-mhdp8546`; provider bindings for `clocks`, `interrupts`, `power-domains`, `phys`, `phy-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/cdns,mhdp8546.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (164 lines). Maintainers listed by the binding: `Swapnil Jakhade <sjakhade@cadence.com>`, `Yuti Amonkar <yamonkar@cadence.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/cdns,mhdp8546.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/chipone,icn6211.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/chipone,icn6211.yaml

## Purpose
Chipone ICN6211 MIPI-DSI to RGB Converter bridge is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `chipone,icn6211.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. ICN6211 is MIPI-DSI to RGB Converter bridge from chipone. It has a flexible configuration of MIPI DSI signal input and produce RGB565, RGB666, RGB888 output format.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/chipone,icn6211.yaml#`, top-level `compatible` values `chipone,icn6211`, required properties `compatible`, `reg`, `enable-gpios`, `ports`, and top-level properties `compatible`, `reg`, `clock-names`, `clocks`, `enable-gpios`, `vdd1-supply`, `vdd2-supply`, `vdd3-supply`, `ports`.
Key property contracts include: `compatible` (enum `chipone,icn6211`); `reg` (maxItems=1; virtual channel number of a DSI peripheral); `clock-names` (const `refclk`); `clocks` (maxItems=1; Optional external clock connected to REF_CLK input. The clock rate must be in 10..154 MHz range.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `chipone,icn6211`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/chipone,icn6211.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (123 lines). Maintainers listed by the binding: `Jagan Teki <jagan@amarulasolutions.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/chipone,icn6211.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/chrontel,ch7033.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/chrontel,ch7033.yaml

## Purpose
Chrontel CH7033 Video Encoder is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `chrontel,ch7033.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Chrontel CH7033 Video Encoder.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/chrontel,ch7033.yaml#`, top-level `compatible` values `chrontel,ch7033`, required properties `compatible`, `reg`, `ports`, and top-level properties `compatible`, `reg`, `ports`.
Key property contracts include: `compatible` (const `chrontel,ch7033`); `reg` (maxItems=1; I2C address of the device); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `chrontel,ch7033`; provider bindings for `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/chrontel,ch7033.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (77 lines). Maintainers listed by the binding: `Lubomir Rintel <lkundrak@v3.sk>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/chrontel,ch7033.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8mp-hdmi-tx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8mp-hdmi-tx.yaml

## Purpose
Freescale i.MX8MP DWC HDMI TX Encoder is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx8mp-hdmi-tx.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The i.MX8MP HDMI transmitter is a Synopsys DesignWare HDMI 2.0a TX controller IP.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx8mp-hdmi-tx.yaml#`, top-level `compatible` values `fsl,imx8mp-hdmi-tx`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `power-domains`, `ports`, and top-level properties `compatible`, `reg-io-width`, `clocks`, `clock-names`, `power-domains`, `ports`.
Key property contracts include: `compatible` (enum `fsl,imx8mp-hdmi-tx`); `clocks` (maxItems=4); `clock-names` (declared by schema); `power-domains` (maxItems=1); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx8mp-hdmi-tx`; provider bindings for `clocks`, `clock-names`, `power-domains`, `ports`.
Referenced shared schemas include `/schemas/display/bridge/synopsys,dw-hdmi.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx8mp-hdmi-tx.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (114 lines). Maintainers listed by the binding: `Lucas Stach <l.stach@pengutronix.de>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8mp-hdmi-tx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-ldb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-ldb.yaml

## Purpose
Freescale i.MX8qm/qxp LVDS Display Bridge is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx8qxp-ldb.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Freescale i.MX8qm/qxp LVDS Display Bridge(LDB) has two channels. The i.MX8qm/qxp LDB is controlled by Control and Status Registers(CSR) module. The CSR module, as a system controller, contains the LDB's configuration registers. For i.MX8qxp LDB, each channel supports up to 24bpp parallel input color format and c...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx8qxp-ldb.yaml#`, top-level `compatible` values `fsl,imx8qm-ldb`, `fsl,imx8qxp-ldb`, required properties `compatible`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`, `power-domains`, `channel@0`, `channel@1`, and top-level properties `compatible`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`, `power-domains`, `fsl,companion-ldb`.
Key property contracts include: `compatible` (enum `fsl,imx8qm-ldb`, `fsl,imx8qxp-ldb`); `#address-cells` (const `1`); `#size-cells` (const `0`); `clocks` (declared by schema); `clock-names` (declared by schema); `power-domains` (maxItems=1); `fsl,companion-ldb` (ref `/schemas/types.yaml#/definitions/phandle`; A phandle which points to companion LDB which is used in LDB split mode.).
The schema also defines pattern properties `^channel@[0-1]$`, which describe child nodes or reusable node fragments.
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx8qm-ldb`, `fsl,imx8qxp-ldb`; provider bindings for `clocks`, `clock-names`, `power-domains`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-ldb.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (173 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-ldb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-combiner.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-combiner.yaml

## Purpose
Freescale i.MX8qm/qxp Pixel Combiner is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx8qxp-pixel-combiner.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Freescale i.MX8qm/qxp Pixel Combiner takes two output streams from a single display controller and manipulates the two streams to support a number of modes(bypass, pixel combine, YUV444 to YUV422, split_RGB) configured as either one screen, two screens, or virtual screens. The pixel combiner is also responsible...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx8qxp-pixel-combiner.yaml#`, top-level `compatible` values `fsl,imx8qm-pixel-combiner`, `fsl,imx8qxp-pixel-combiner`, required properties `compatible`, `#address-cells`, `#size-cells`, `reg`, `clocks`, `clock-names`, `power-domains`, and top-level properties `compatible`, `#address-cells`, `#size-cells`, `reg`, `clocks`, `clock-names`, `power-domains`.
Key property contracts include: `compatible` (enum `fsl,imx8qm-pixel-combiner`, `fsl,imx8qxp-pixel-combiner`); `#address-cells` (const `1`); `#size-cells` (const `0`); `reg` (maxItems=1); `clocks` (maxItems=1); `clock-names` (const `apb`); `power-domains` (maxItems=1).
The schema also defines pattern properties `^channel@[0-1]$`, which describe child nodes or reusable node fragments.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx8qm-pixel-combiner`, `fsl,imx8qxp-pixel-combiner`; provider bindings for `clocks`, `clock-names`, `power-domains`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-combiner.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (144 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-combiner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-link.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-link.yaml

## Purpose
Freescale i.MX8qm/qxp Display Pixel Link is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx8qxp-pixel-link.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Freescale i.MX8qm/qxp Display Pixel Link(DPL) forms a standard asynchronous linkage between pixel sources(display controller or camera module) and pixel consumers(imaging or displays). It consists of two distinct functions, a pixel transfer function and a control interface. Multiple pixel channels can exist per...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx8qxp-pixel-link.yaml#`, top-level `compatible` values `fsl,imx8qm-dc-pixel-link`, `fsl,imx8qxp-dc-pixel-link`, required properties `compatible`, `fsl,dc-id`, `fsl,dc-stream-id`, `ports`, and top-level properties `compatible`, `fsl,dc-id`, `fsl,dc-stream-id`, `ports`.
Key property contracts include: `compatible` (enum `fsl,imx8qm-dc-pixel-link`, `fsl,imx8qxp-dc-pixel-link`); `fsl,dc-id` (ref `/schemas/types.yaml#/definitions/uint8`; u8 value representing the display controller index that the pixel link connects to.); `fsl,dc-stream-id` (enum `0`, `1`; ref `/schemas/types.yaml#/definitions/uint8`; u8 value representing the display controller stream index that the pixel link connects to.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx8qm-dc-pixel-link`, `fsl,imx8qxp-dc-pixel-link`; provider bindings for `ports`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint8`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-link.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (144 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pixel-link.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pxl2dpi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pxl2dpi.yaml

## Purpose
Freescale i.MX8qxp Pixel Link to Display Pixel Interface is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx8qxp-pxl2dpi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The Freescale i.MX8qxp Pixel Link to Display Pixel Interface(PXL2DPI) interfaces the pixel link 36-bit data output and the DSI controller’s MIPI-DPI 24-bit data input, and inputs of LVDS Display Bridge(LDB) module used in LVDS mode, to remap the pixel color codings between those modules. This module is purely combin...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx8qxp-pxl2dpi.yaml#`, top-level `compatible` values `fsl,imx8qxp-pxl2dpi`, required properties `compatible`, `fsl,sc-resource`, `power-domains`, `ports`, and top-level properties `compatible`, `fsl,sc-resource`, `power-domains`, `fsl,companion-pxl2dpi`, `ports`.
Key property contracts include: `compatible` (const `fsl,imx8qxp-pxl2dpi`); `fsl,sc-resource` (ref `/schemas/types.yaml#/definitions/uint32`; The SCU resource ID associated with this PXL2DPI instance.); `power-domains` (maxItems=1); `fsl,companion-pxl2dpi` (ref `/schemas/types.yaml#/definitions/phandle`; A phandle which points to companion PXL2DPI which is used by downstream LVDS Display Bridge(LDB) in split mode.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx8qxp-pxl2dpi`; provider bindings for `power-domains`, `ports`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pxl2dpi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (108 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx8qxp-pxl2dpi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx93-mipi-dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx93-mipi-dsi.yaml

## Purpose
Freescale i.MX93 specific extensions to Synopsys Designware MIPI DSI is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,imx93-mipi-dsi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. There is a Synopsys Designware MIPI DSI Host Controller and a Synopsys Designware MIPI DPHY embedded in Freescale i.MX93 SoC. Some configurations and extensions to them are controlled by i.MX93 media blk-ctrl.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,imx93-mipi-dsi.yaml#`, top-level `compatible` values `fsl,imx93-mipi-dsi`, required properties `compatible`, `interrupts`, `fsl,media-blk-ctrl`, `power-domains`, and top-level properties `compatible`, `clocks`, `clock-names`, `interrupts`, `fsl,media-blk-ctrl`, `power-domains`.
Key property contracts include: `compatible` (const `fsl,imx93-mipi-dsi`); `clocks` (declared by schema); `clock-names` (declared by schema); `interrupts` (maxItems=1); `fsl,media-blk-ctrl` (ref `/schemas/types.yaml#/definitions/phandle`; i.MX93 media blk-ctrl, as a syscon, controls pixel component bit map configurations from LCDIF display controller to the MIPI DSI host controller and MIPI DPHY PLL related configurations through PLL SoC interface.); `power-domains` (maxItems=1).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx93-mipi-dsi`; provider bindings for `clocks`, `clock-names`, `interrupts`, `power-domains`.
Referenced shared schemas include `snps,dw-mipi-dsi.yaml#`, `/schemas/types.yaml#/definitions/phandle`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,imx93-mipi-dsi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (115 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,imx93-mipi-dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,ldb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,ldb.yaml

## Purpose
Freescale i.MX8MP DPI to LVDS bridge chip is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `fsl,ldb.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The i.MX8MP mediamix contains two registers which are responsible for configuring the on-SoC DPI-to-LVDS serializer. This describes those registers as bridge within the DT.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/fsl,ldb.yaml#`, top-level `compatible` values `fsl,imx6sx-ldb`, `fsl,imx8mp-ldb`, `fsl,imx93-ldb`, required properties `compatible`, `clocks`, `ports`, `reg`, and top-level properties `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `nxp,enable-termination-resistor`, `ports`.
Key property contracts include: `compatible` (enum `fsl,imx6sx-ldb`, `fsl,imx8mp-ldb`, `fsl,imx93-ldb`); `clocks` (maxItems=1); `clock-names` (const `ldb`); `reg` (maxItems=2); `nxp,enable-termination-resistor` (Indicates that the built-in 100 Ohm termination resistor on the LVDS output is enabled. This property is optional and controlled via the HS_EN bit in the LVDS_CTRL register. Enabling it can improve signal quality and prevent visual artifacts on some boards, but increases power consumption.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `fsl,imx6sx-ldb`, `fsl,imx8mp-ldb`, `fsl,imx93-ldb`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/fsl,ldb.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (150 lines). Maintainers listed by the binding: `Marek Vasut <marex@denx.de>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/fsl,ldb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/google,cros-ec-anx7688.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/google,cros-ec-anx7688.yaml

## Purpose
ChromeOS EC ANX7688 HDMI to DP Converter through Type-C Port is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `google,cros-ec-anx7688.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. ChromeOS EC ANX7688 is a display bridge that converts HDMI 2.0 to DisplayPort 1.3 Ultra-HDi (4096x2160p60). It is an Analogix ANX7688 chip which is connected to and operated by the ChromeOS Embedded Controller (See google,cros-ec.yaml). It is accessed using I2C tunneling through the EC and therefore its node should...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/google,cros-ec-anx7688.yaml#`, top-level `compatible` values `google,cros-ec-anx7688`, required properties `compatible`, `reg`, `ports`, and top-level properties `compatible`, `reg`, `ports`.
Key property contracts include: `compatible` (const `google,cros-ec-anx7688`); `reg` (maxItems=1; I2C address of the device.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `google,cros-ec-anx7688`; provider bindings for `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/google,cros-ec-anx7688.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (80 lines). Maintainers listed by the binding: `Nicolas Boichat <drinkcat@chromium.org>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/google,cros-ec-anx7688.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ingenic,jz4780-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ingenic,jz4780-hdmi.yaml

## Purpose
Ingenic JZ4780 HDMI Transmitter is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ingenic,jz4780-hdmi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The HDMI Transmitter in the Ingenic JZ4780 is a Synopsys DesignWare HDMI 1.4 TX controller IP with accompanying PHY IP.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/ingenic,jz4780-hdmi.yaml#`, top-level `compatible` values `ingenic,jz4780-dw-hdmi`, required properties `compatible`, `clocks`, `clock-names`, `ports`, `reg-io-width`, and top-level properties `compatible`, `reg-io-width`, `clocks`, `clock-names`, `ports`.
Key property contracts include: `compatible` (const `ingenic,jz4780-dw-hdmi`); `clocks` (maxItems=2); `clock-names` (maxItems=2); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `ingenic,jz4780-dw-hdmi`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `synopsys,dw-hdmi.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ingenic,jz4780-hdmi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (84 lines). Maintainers listed by the binding: `H. Nikolaus Schaller <hns@goldelico.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ingenic,jz4780-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/intel,keembay-dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/intel,keembay-dsi.yaml

## Purpose
Intel Keem Bay mipi dsi controller is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `intel,keembay-dsi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. DeviceTree schema for Intel Keem Bay mipi dsi controller.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/intel,keembay-dsi.yaml#`, top-level `compatible` values `intel,keembay-dsi`, required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `ports`, and top-level properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `ports`.
Key property contracts include: `compatible` (const `intel,keembay-dsi`); `reg` (declared by schema); `clocks` (declared by schema); `clock-names` (declared by schema); `ports` (ref `/schemas/graph.yaml#/properties/ports`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `intel,keembay-dsi`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/intel,keembay-dsi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (93 lines). Maintainers listed by the binding: `Anitha Chrisanthus <anitha.chrisanthus@intel.com>`, `Edmond J Dea <edmund.j.dea@intel.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/intel,keembay-dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it6263.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it6263.yaml

## Purpose
ITE IT6263 LVDS to HDMI converter is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ite,it6263.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The IT6263 is a high-performance single-chip De-SSC(De-Spread Spectrum) LVDS to HDMI converter. Combined with LVDS receiver and HDMI 1.4a transmitter, the IT6263 supports LVDS input and HDMI 1.4 output by conversion function. The built-in LVDS receiver can support single-link and dual-link LVDS inputs, and the built...

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/ite,it6263.yaml#`, top-level `compatible` values `ite,it6263`, required properties `compatible`, `reg`, `data-mapping`, `ivdd-supply`, `ovdd-supply`, `txavcc18-supply`, `txavcc33-supply`, `pvcc1-supply`, `pvcc2-supply`, `avcc-supply`, `anvdd-supply`, `apvdd-supply`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `data-mapping`, `reset-gpios`, `ivdd-supply`, `ovdd-supply`, `txavcc18-supply`, `txavcc33-supply`, `pvcc1-supply`, `pvcc2-supply`, `avcc-supply`, `anvdd-supply`, `apvdd-supply`, `#sound-dai-cells`, `ite,i2s-audio-fifo-sources`, `ite,rl-channel-swap-audio-sources`, and 1 more.
Key property contracts include: `compatible` (const `ite,it6263`); `reg` (maxItems=1); `clocks` (maxItems=1; audio master clock); `clock-names` (const `mclk`); `#sound-dai-cells` (const `0`); `ite,i2s-audio-fifo-sources` (maxItems=4; minItems=1; ref `/schemas/types.yaml#/definitions/uint32-array`; Each array element indicates the pin number of an I2S serial data input line which is connected to an audio FIFO, from audio FIFO0 to FIFO3.); `ite,rl-channel-swap-audio-sources` (maxItems=4; minItems=1; ref `/schemas/types.yaml#/definitions/uint32-array`; Each array element indicates an audio source whose right channel and left channel are swapped by this converter. For I2S, the element is the pin number of an I2S serial data input line. For S/PDIF, the element is always 0.); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `ite,it6263`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `/schemas/display/lvds-dual-ports.yaml#`, `/schemas/sound/dai-common.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ite,it6263.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 2 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (251 lines). Maintainers listed by the binding: `Liu Ying <victor.liu@nxp.com>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ite,it6263.yaml -->
