# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,pl330.yaml

## Purpose
This file is a Linux Devicetree binding schema for ARM PrimeCell PL330 DMA Controller. It validates nodes matched by `arm,pl330`. Source description: The ARM PrimeCell PL330 DMA controller can move blocks of memory contents In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/arm,pl330.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `arm,pl330`. Required properties: `compatible`, `reg`, `interrupts`. Notable properties: `compatible`, `reg`, `interrupts`, `arm,pl330-broken-no-flushp`, `arm,pl330-periph-burst`, `dma-coherent`, `iommus`, `power-domains`, `resets`, `reset-names`. Referenced schemas: `dma-controller.yaml#`, `/schemas/arm/primecell.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `dma-controller@12680000` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, /schemas/arm/primecell.yaml#, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,pl330.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,pl330.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
