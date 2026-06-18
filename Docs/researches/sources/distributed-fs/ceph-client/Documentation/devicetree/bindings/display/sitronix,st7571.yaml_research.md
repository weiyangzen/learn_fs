# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7571.yaml

## Purpose
This file is a Linux Devicetree binding schema for Sitronix ST7571 Display Controller. It validates nodes matched by `sitronix,st7571`. Source description: Sitronix ST7571 is a driver and controller for 4-level gray In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sitronix,st7571.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sitronix,st7571`. Required properties: `compatible`, `reg`, `reset-gpios`, `width-mm`, `height-mm`, `panel-timing`. Notable properties: `compatible`, `reg`, `sitronix,grayscale`, `sitronix,inverted`, `reset-gpios`, `width-mm`, `height-mm`, `panel-timing`. Referenced schemas: `panel/panel-common.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `i2c` and exercises the main required properties with 1 dt-bindings include(s).

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, panel/panel-common.yaml#, reset/GPIO bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7571.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7571.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
