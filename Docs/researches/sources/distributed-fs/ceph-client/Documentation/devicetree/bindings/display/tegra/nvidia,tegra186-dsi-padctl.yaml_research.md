# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dsi-padctl.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra MIPI DSI pad controller. It validates nodes matched by `nvidia,tegra186-dsi-padctl`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra186-dsi-padctl.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra186-dsi-padctl`. Required properties: none. Notable properties: `compatible`, `reg`, `resets`, `reset-names`. Referenced schemas: `/schemas/reset/reset.yaml`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `padctl@15880000` and exercises the main required properties with 1 dt-bindings include(s).

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/reset/reset.yaml, reset/GPIO bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dsi-padctl.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dsi-padctl.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
