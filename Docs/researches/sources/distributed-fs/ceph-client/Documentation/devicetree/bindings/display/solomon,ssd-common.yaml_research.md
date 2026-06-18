# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd-common.yaml

## Purpose
This file is a Linux Devicetree binding schema for Common properties for Solomon OLED Display Controllers. It is a reusable schema fragment consumed by concrete bindings rather than a standalone compatible match. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/solomon,ssd-common.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: none. Required properties: none. Notable properties: `reg`, `reset-gpios`, `dc-gpios`, `solomon,height`, `solomon,width`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/spi/spi-peripheral-props.yaml#`. Validation keywords and constraints: allOf. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: This is a reusable schema fragment rather than a concrete driver match table.

## Control Flow
Concrete schemas include this fragment with `$ref`/`allOf`; validation then flows through the shared rules defined here. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/spi/spi-peripheral-props.yaml#, reset/GPIO bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are schema drift from driver expectations or from existing in-tree DTS users.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd-common.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd-common.yaml` against in-tree DTS users, example-schema validation from the `examples` block.
