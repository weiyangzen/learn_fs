<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel,keembay.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel,keembay.yaml

## Purpose
This schema identifies Intel Keem Bay platform DT root nodes.

## Important APIs, Types, And Functions
It fixes `$nodename` to `/` and requires `compatible = "intel,keembay-evm", "intel,keembay"`.

## Control Flow
Validation is a simple ordered `items` check. The board-specific compatible must precede the SoC fallback.

## State And Persistence
The schema describes immutable platform identity only. There is no runtime state, allocation, or persistence behavior.

## Dependencies And Integration Points
It integrates with Keem Bay board selection and SoC driver matching through the root compatible list.

## Risks
The binding currently covers one EVM; derivative boards need explicit schema updates. Misordering the two compatibles can break generic Keem Bay matching.

## Test Signals
`dt_binding_check` validates the schema and `dtbs_check` validates any Keem Bay DTS root node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel,keembay.yaml -->
