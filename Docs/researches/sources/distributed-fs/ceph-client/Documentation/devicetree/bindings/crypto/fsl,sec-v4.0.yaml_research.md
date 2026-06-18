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
