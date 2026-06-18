# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd1307fb.yaml

## Purpose
This file is a Linux Devicetree binding schema for Solomon SSD1307 OLED Controller Framebuffer. It validates nodes matched by `solomon,ssd1305fb-i2c`, `solomon,ssd1306fb-i2c`, `solomon,ssd1307fb-i2c`, `solomon,ssd1309fb-i2c`, `sinowealth,sh1106`, `solomon,ssd1305`, `solomon,ssd1306`, `solomon,ssd1307`, and 1 more. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/solomon,ssd1307fb.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `solomon,ssd1305fb-i2c`, `solomon,ssd1306fb-i2c`, `solomon,ssd1307fb-i2c`, `solomon,ssd1309fb-i2c`, `sinowealth,sh1106`, `solomon,ssd1305`, `solomon,ssd1306`, `solomon,ssd1307`, `solomon,ssd1309`. Required properties: `compatible`, `reg`. Notable properties: `compatible`, `pwms`, `vbat-supply`, `solomon,page-offset`, `solomon,segment-no-remap`, `solomon,col-offset`, `solomon,com-seq`, `solomon,com-lrremap`, `solomon,com-invdir`, `solomon,com-offset`, `solomon,prechargep1`, `solomon,prechargep2`, `solomon,dclk-div`, `solomon,dclk-frq`, `solomon,lookup-table`, `solomon,area-color-enable`, `solomon,low-power`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint8-array`, `solomon,ssd-common.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then, deprecated: true. The example instantiates `i2c` and exercises the main required properties. File-specific integration notes: The schema preserves deprecated properties for legacy DTS compatibility while steering new users toward common bindings. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint8-array, solomon,ssd-common.yaml#, PWM bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; deprecated properties must remain accepted long enough for old DTS files while new bindings avoid them; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd1307fb.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd1307fb.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
