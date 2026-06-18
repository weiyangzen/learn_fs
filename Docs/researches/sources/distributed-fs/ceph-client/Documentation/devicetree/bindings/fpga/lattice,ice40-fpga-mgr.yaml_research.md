<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,ice40-fpga-mgr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,ice40-fpga-mgr.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Lattice iCE40 FPGA Manager. Lattice iCE40 FPGA Manager

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/lattice,ice40-fpga-mgr.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Lattice iCE40 FPGA Manager`.
- Compatible strings or compatible constants enumerated by the schema include `lattice,ice40-fpga-mgr`.
- Top-level required properties: `compatible`, `reg`, `spi-max-frequency`, `cdone-gpios`, `reset-gpios`.
- `compatible`: const `lattice,ice40-fpga-mgr`.
- `reg`: maxItems 1.
- `spi-max-frequency`: constraints via minimum, maximum.
- `cdone-gpios`: GPIO input connected to CDONE pin; maxItems 1.
- `reset-gpios`: Active-low GPIO output connected to CRESET_B pin. Note that unless the GPIO is held low during startup, the FPGA...; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `reset-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/lattice,ice40-fpga-mgr.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lattice,ice40-fpga-mgr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,ice40-fpga-mgr.yaml -->
