<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-hps2fpga-bridge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-hps2fpga-bridge.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Altera FPGA/HPS Bridge. Altera FPGA/HPS Bridge

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/altr,socfpga-hps2fpga-bridge.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Altera FPGA/HPS Bridge`.
- Compatible strings or compatible constants enumerated by the schema include `altr,socfpga-lwhps2fpga-bridge`, `altr,socfpga-hps2fpga-bridge`, `altr,socfpga-fpga2hps-bridge`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `resets`.
- `compatible`: enum `altr,socfpga-lwhps2fpga-bridge`, `altr,socfpga-hps2fpga-bridge`, `altr,socfpga-fpga2hps-bridge`.
- `reg`: maxItems 1.
- `resets`: maxItems 1.
- `clocks`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fpga-bridge.yaml#`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/altr,socfpga-hps2fpga-bridge.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `altr,socfpga-lwhps2fpga-bridge`, `altr,socfpga-hps2fpga-bridge`, `altr,socfpga-fpga2hps-bridge`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-hps2fpga-bridge.yaml -->
