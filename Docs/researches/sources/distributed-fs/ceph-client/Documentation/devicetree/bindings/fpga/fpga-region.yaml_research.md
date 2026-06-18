<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-region.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-region.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for FPGA Region. CONTENTS - Introduction - Terminology - Sequence - FPGA Region - Supported Use Models - Constraints Introduction ============ FPGA Regions represent FPGA's and partial reconfiguration regions of FPGA's in the Device Tree. FPGA Regions provide a way to program FPGAs under device tree control. The documentation hits some of the high points of FPGA usage and attempts to include terminology used by both major FPGA manufacturers. This document isn't a replacement for any manufacturers specifications for FPGA usage..

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/fpga-region.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `FPGA Region`.
- Top-level required properties: `compatible`, `fpga-mgr`.
- `$nodename`: pattern `^fpga-region(@.*|-([0-9]|[1-9][0-9]+))?$`.
- `compatible`: const `fpga-region`.
- `reg`: maxItems 1.
- `ranges` is accepted as a flag/property marker.
- `#address-cells` is accepted as a flag/property marker.
- `#size-cells` is accepted as a flag/property marker.
- `config-complete-timeout-us`: The maximum time in microseconds time for the FPGA to go to operating mode after the region has been programmed..
- `encrypted-fpga-config`: Set if the bitstream is encrypted..
- `external-fpga-config`: Set if the FPGA has already been configured prior to OS boot up..
- `firmware-name`: Should contain the name of an FPGA image file located on the firmware search path. If this property shows up in a...; maxItems 1.
- `fpga-bridges`: Should contain a list of phandles to FPGA Bridges that must be controlled during FPGA programming along with the...; ref `/schemas/types.yaml#/definitions/phandle-array`.
- `fpga-mgr`: Should contain a phandle to an FPGA Manager. Child FPGA Regions inherit this property from their ancestor regions....; ref `/schemas/types.yaml#/definitions/phandle`.
- `partial-fpga-config`: Set if partial reconfiguration is to be done, otherwise full reconfiguration is done..
- `region-freeze-timeout-us`: The maximum time in microseconds to wait for bridges to successfully become disabled before the region has been....
- `region-unfreeze-timeout-us`: The maximum time in microseconds to wait for bridges to successfully become enabled after the region has been....

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `{'type': 'object'}`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/phandle`.
- Integrates with provider/consumer property `reg`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/fpga-region.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-region.yaml -->
