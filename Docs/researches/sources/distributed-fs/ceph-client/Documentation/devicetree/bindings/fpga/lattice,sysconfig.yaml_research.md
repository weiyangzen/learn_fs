<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,sysconfig.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,sysconfig.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Lattice Slave SPI sysCONFIG FPGA manager. Lattice sysCONFIG port, which is used for FPGA configuration, among others, have Slave Serial Peripheral Interface. Only full reconfiguration is supported. Programming of ECP5 is done by writing uncompressed bitstream image in .bit format into FPGA's SRAM configuration memory.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/lattice,sysconfig.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Lattice Slave SPI sysCONFIG FPGA manager`.
- Compatible strings or compatible constants enumerated by the schema include `lattice,sysconfig-ecp5`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: enum `lattice,sysconfig-ecp5`.
- `reg`: maxItems 1.
- `program-gpios`: A GPIO line connected to PROGRAMN (active low) pin of the device. Initiates configuration sequence.; maxItems 1.
- `init-gpios`: A GPIO line connected to INITN (active low) pin of the device. Indicates that the FPGA is ready to be configured.; maxItems 1.
- `done-gpios`: A GPIO line connected to DONE (active high) pin of the device. Indicates that the configuration sequence is...; maxItems 1.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/lattice,sysconfig.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lattice,sysconfig-ecp5`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,sysconfig.yaml -->
