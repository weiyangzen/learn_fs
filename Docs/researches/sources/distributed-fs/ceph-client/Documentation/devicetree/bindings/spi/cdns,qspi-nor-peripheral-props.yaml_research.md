<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor-peripheral-props.yaml

## Purpose
Devicetree binding schema fragment for Peripheral-specific properties for the Cadence QSPI controller. in the Linux SPI subsystem. It documents reusable node properties rather than a single top-level compatible. The schema description narrows this to: See spi-peripheral-props.yaml for more info.

## Important APIs/types/functions
- Schema property keys observed: `cdns,read-delay`, `cdns,tshsl-ns`, `cdns,tsd2d-ns`, `cdns,tchsh-ns`, `cdns,tslch-ns`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are none declared. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Vaishnav Achath <vaishnav.a@ti.com>.

## Risks and edge cases
as a reusable or permissive schema, weak required-property coverage can allow incomplete nodes through validation; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/cdns,qspi-nor-peripheral-props.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; coverage depends on consumer schemas and real DTS users because this file has no embedded example block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor-peripheral-props.yaml -->
