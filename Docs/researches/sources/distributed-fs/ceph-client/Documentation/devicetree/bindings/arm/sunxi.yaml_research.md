<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi.yaml

## Purpose
This large root-node schema catalogs Allwinner/Sunxi boards across A-series, H-series, R-series, V-series, F-series, T-series, and related SoC families.

## Important APIs, Types, And Functions
It validates a very large set of board-to-SoC compatible chains for tablets, SBCs, TV boxes, routers, embedded modules, EVBs, Pine64/Orange Pi/Banana Pi/Libretech/Lichee/OLinuXino products, and many vendor boards. Fallbacks include SoC strings such as `allwinner,sun4i-a10`, `sun5i-a13`, `sun7i-a20`, `sun8i-*`, `sun9i-a80`, `sun20i-d1`, `sun50i-*`, and others.

## Control Flow
`oneOf` selects one exact compatible branch and enforces ordering from specific board or module through generic SoC fallback. `additionalProperties: true` leaves other root-node fields to generic validation.

## State And Persistence
The schema stores immutable platform identity only. Peripheral resources and runtime state live in child nodes and drivers.

## Dependencies And Integration Points
It integrates with the broad Sunxi DTS tree, board-specific quirks, and Allwinner SoC/platform matching.

## Risks
The catalog is large and high-churn. Similar board names and multiple SoC generations make wrong fallback chains likely when adding entries. Maintaining stable compatibles is important because bootloaders and kernels rely on them.

## Test Signals
`dtbs_check` across Sunxi DTBs is the primary validation. Runtime signals include correct board detection, regulator/peripheral initialization, and successful boot on representative boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi.yaml -->
