# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr3d.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA 3D graphics engine. It validates nodes matched by `nvidia,tegra20-gr3d`, `nvidia,tegra30-gr3d`, `nvidia,tegra114-gr3d`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-gr3d.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-gr3d`, `nvidia,tegra30-gr3d`, `nvidia,tegra114-gr3d`. Required properties: none. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `iommus`, `interconnects`, `interconnect-names`, `operating-points-v2`, `power-domains`, `power-domain-names`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false, allOf, if, then. The example instantiates `gr3d@54180000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr3d.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr3d.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
