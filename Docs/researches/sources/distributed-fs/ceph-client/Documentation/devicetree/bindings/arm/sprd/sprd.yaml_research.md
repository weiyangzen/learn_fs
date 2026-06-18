<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sprd/sprd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sprd/sprd.yaml

## Purpose
This root platform schema catalogs Spreadtrum/Unisoc ARM boards.

## Important APIs, Types, And Functions
It validates compatible chains for SC9860G-1H10, SC9863A boards including Unisoc UMS512-1H10 and Samsung Galaxy A03 Core, Sharkl3, and UMS9620 boards.

## Control Flow
The root node name is `/`; `oneOf` selects the board/SoC branch and enforces exact ordering.

## State And Persistence
It stores immutable board and SoC identity only.

## Dependencies And Integration Points
It integrates with SPRD/Unisoc DTS files and platform matching.

## Risks
Vendor naming has changed over time, so board additions must preserve existing Spreadtrum/Unisoc compatible conventions. Wrong fallback can affect SoC driver matching.

## Test Signals
`dtbs_check` validates root compatible strings; boot and platform probe validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sprd/sprd.yaml -->
