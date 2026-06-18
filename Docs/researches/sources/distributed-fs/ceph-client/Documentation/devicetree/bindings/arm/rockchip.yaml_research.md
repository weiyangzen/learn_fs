<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip.yaml

## Purpose
This large root platform schema catalogs Rockchip boards across RK30xx, RK31xx, RK32xx, RK33xx, RK35xx, RV11xx, PX30, RK3576, RK3588/RK3588S, and related families.

## Important APIs, Types, And Functions
It fixes `$nodename` to `/` and validates hundreds of exact compatible chains for SBCs, Chromebooks, tablets, handheld consoles, NAS/router boards, SOM/carrier combinations, EVBs, and vendor products. Many chains encode board variants, module fallbacks, Google ChromeOS revision chains, and SoC fallbacks such as `rockchip,rk3399`, `rk3566`, `rk3568`, `rk3576`, `rk3588`, and `rk3588s`.

## Control Flow
dt-schema selects one `oneOf` branch and enforces all compatible strings in order. Long ChromeOS and SOM chains preserve a hierarchy from exact revision through product family to generic SoC.

## State And Persistence
The schema stores immutable board identity only. Runtime resources and device state live in peripheral nodes and drivers.

## Dependencies And Integration Points
It integrates with Rockchip DTS files, platform matching, board-specific quirks, and SoC driver selection across a wide product set.

## Risks
The table is very large and high-churn. Similar product names, revision chains, and RK3588/RK3588S/RK3576 distinctions make accidental fallback changes a real compatibility risk.

## Test Signals
`dtbs_check` over Rockchip DTBs is essential. Runtime platform match, regulator/peripheral probe, and boot on representative boards validate the compatible chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip.yaml -->
