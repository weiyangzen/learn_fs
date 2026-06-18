# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vip.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra VIP (parallel video capture) controller. It validates nodes matched by `nvidia,tegra20-vip`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-vip.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-vip`. Required properties: `compatible`, `ports`. Notable properties: `compatible`, `ports`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: unevaluatedProperties: false. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vip.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vip.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
