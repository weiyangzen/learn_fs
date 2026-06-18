# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-dpaux.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra DisplayPort AUX Interface. It validates nodes matched by `nvidia,tegra124-dpaux`, `nvidia,tegra210-dpaux`, `nvidia,tegra186-dpaux`, `nvidia,tegra194-dpaux`. Source description: The Tegra Display Port Auxiliary (DPAUX) pad controller manages two pins which can be assigned to either the DPAUX channel or to an I2C controller. When configured for DisplayPort AUX operation, the DPAUX controller can also be used to communicate with a DisplayPort device using the AUX channel. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra124-dpaux.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra124-dpaux`, `nvidia,tegra210-dpaux`, `nvidia,tegra186-dpaux`, `nvidia,tegra194-dpaux`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `i2c-bus`, `aux-bus`, `vdd-supply`. Referenced schemas: `/schemas/display/dp-aux-bus.yaml#`. Validation keywords and constraints: additionalProperties: false, patternProperties. The example instantiates `i2c-bus` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/display/dp-aux-bus.yaml#, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-dpaux.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-dpaux.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
