<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fuse/nvidia,tegra20-fuse.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fuse/nvidia,tegra20-fuse.yaml

## Purpose
This YAML binding defines the Device Tree contract for the eFuse/SoC fuse binding for NVIDIA Tegra FUSE block. NVIDIA Tegra FUSE block

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fuse/nvidia,tegra20-fuse.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NVIDIA Tegra FUSE block`.
- Compatible strings or compatible constants enumerated by the schema include `nvidia,tegra20-efuse`, `nvidia,tegra30-efuse`, `nvidia,tegra114-efuse`, `nvidia,tegra124-efuse`, `nvidia,tegra210-efuse`, `nvidia,tegra186-efuse`, `nvidia,tegra194-efuse`, `nvidia,tegra234-efuse`, `nvidia,tegra132-efuse`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `clock-names`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `clock-names`: 1 ordered items.
- `resets`: maxItems 1.
- `reset-names`: 1 ordered items.
- `operating-points-v2` is accepted as a flag/property marker.
- `power-domains`: 1 ordered items.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates SoC fuse/NVMEM layout nodes; runtime consumers usually read calibration, identification, or production strap data through nvmem cells.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The binding describes read-only fuse register windows and NVMEM child cells; durable values live in silicon fuses, not in the schema.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `resets`.
- Integrates with provider/consumer property `power-domains`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fuse/nvidia,tegra20-fuse.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nvidia,tegra20-efuse`, `nvidia,tegra30-efuse`, `nvidia,tegra114-efuse`, `nvidia,tegra124-efuse`, `nvidia,tegra210-efuse`, `nvidia,tegra186-efuse`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fuse/nvidia,tegra20-fuse.yaml -->
