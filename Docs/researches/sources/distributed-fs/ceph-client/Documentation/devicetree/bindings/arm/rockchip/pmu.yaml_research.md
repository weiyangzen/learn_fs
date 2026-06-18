<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip/pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip/pmu.yaml

## Purpose
This schema describes Rockchip Power Management Unit syscon blocks used to control SoC power domains, including CPU-core power.

## Important APIs, Types, And Functions
It selects Rockchip PMU compatibles for PX30, RK3066, RK3128, RK3288, RK3368, RK3399, RK3528, RK3562, RK3568, RK3576, RK3588, and RV1126. Compatible must be the SoC-specific PMU string followed by `syscon` and `simple-mfd`. Required properties are `compatible` and `reg`; optional child objects include `power-controller` and `reboot-mode`.

## Control Flow
The `select` block targets PMU compatibles. Validation requires a three-item compatible chain and one register resource, while permitting only declared child objects.

## State And Persistence
The DT records PMU registers and optional child functions. Runtime state is in syscon, power-domain, and reboot-mode drivers.

## Dependencies And Integration Points
It integrates with Rockchip power-domain controllers, reboot-mode handling, and syscon/simple-mfd infrastructure.

## Risks
Missing `simple-mfd` can prevent child devices from probing. Wrong PMU register range can affect power-domain control and reboot behavior.

## Test Signals
`dtbs_check` validates PMU nodes. Runtime signals include power-domain registration, suspend/resume behavior, and reboot-mode operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip/pmu.yaml -->
