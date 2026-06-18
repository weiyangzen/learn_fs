# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7920.yaml

## Purpose
This file is a Linux Devicetree binding schema for Sitronix ST7920 LCD Display Controllers. It validates nodes matched by `sitronix,st7920`. Source description: The Sitronix ST7920 is a controller for monochrome dot-matrix graphical LCDs, In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sitronix,st7920.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sitronix,st7920`. Required properties: `compatible`, `reg`, `spi-max-frequency`. Notable properties: `compatible`, `reg`, `vdd-supply`, `reset-gpios`, `spi-max-frequency`. Referenced schemas: `/schemas/spi/spi-peripheral-props.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `spi` and exercises the main required properties with 1 dt-bindings include(s).

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/spi/spi-peripheral-props.yaml#, reset/GPIO bindings, SPI peripheral properties. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7920.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7920.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
