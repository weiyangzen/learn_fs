<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-selectmap.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-selectmap.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Xilinx SelectMAP FPGA interface. Xilinx 7 Series FPGAs support a method of loading the bitstream over a parallel port named the SelectMAP interface in the documentation. Only the x8 mode is supported where data is loaded at one byte per rising edge of the clock, with the MSB of each byte presented to the D0 pin. Datasheets: https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/xlnx,fpga-selectmap.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx SelectMAP FPGA interface`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,fpga-xc7s-selectmap`, `xlnx,fpga-xc7a-selectmap`, `xlnx,fpga-xc7k-selectmap`, `xlnx,fpga-xc7v-selectmap`.
- Top-level required properties: `compatible`, `reg`, `prog-gpios`, `done-gpios`, `init-gpios`.
- `compatible`: enum `xlnx,fpga-xc7s-selectmap`, `xlnx,fpga-xc7a-selectmap`, `xlnx,fpga-xc7k-selectmap`, `xlnx,fpga-xc7v-selectmap`.
- `reg`: At least 1 byte of memory mapped IO; maxItems 1.
- `prog-gpios`: config pin (referred to as PROGRAM_B in the manual); maxItems 1.
- `done-gpios`: config status pin (referred to as DONE in the manual); maxItems 1.
- `init-gpios`: initialization status and configuration error pin (referred to as INIT_B in the manual); maxItems 1.
- `csi-gpios`: chip select pin (referred to as CSI_B in the manual) Optional gpio for if the bus controller does not provide a...; maxItems 1.
- `rdwr-gpios`: read/write select pin (referred to as RDWR_B in the manual) Optional gpio for if the bus controller does not...; maxItems 1.
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
- References shared schemas: `/schemas/memory-controllers/mc-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/xlnx,fpga-selectmap.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,fpga-xc7s-selectmap`, `xlnx,fpga-xc7a-selectmap`, `xlnx,fpga-xc7k-selectmap`, `xlnx,fpga-xc7v-selectmap`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-selectmap.yaml -->
