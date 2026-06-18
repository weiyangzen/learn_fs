<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar.yaml

## Purpose
This root platform schema catalogs MStar/SigmaStar boards for Infinity, Infinity2M, Infinity3, and Mercury5 SoC families.

## Important APIs, Types, And Functions
The root compatible list maps boards such as BreadBee, BreadBee Crust, DongShanPiOne, UnitV2, Miyoo Mini, Wireless Tag modules, and 70mai midrive d08 to their SoC family fallback.

## Control Flow
`oneOf` selects the SoC family branch and validates exact board-to-SoC compatible ordering.

## State And Persistence
It records immutable platform identity only.

## Dependencies And Integration Points
It integrates with MStar DTS files and platform matching for these SoCs.

## Risks
The schema covers small-board ecosystems where board names are similar; incorrect enum placement can select wrong SoC support.

## Test Signals
`dtbs_check` validates root compatible chains; board boot validates platform matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar.yaml -->
