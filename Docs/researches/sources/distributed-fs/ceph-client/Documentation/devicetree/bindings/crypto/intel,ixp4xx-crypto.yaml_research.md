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
