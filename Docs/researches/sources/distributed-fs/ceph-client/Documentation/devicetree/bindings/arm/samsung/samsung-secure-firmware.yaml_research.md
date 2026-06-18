<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-secure-firmware.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-secure-firmware.yaml

## Purpose
This binding describes Samsung secure firmware nodes used as a conduit for secure monitor services.

## Important APIs, Types, And Functions
The schema requires `compatible = "samsung,secure-firmware"` and a single `reg` range.

## Control Flow
Validation is strict, requiring compatible and reg while rejecting additional properties.

## State And Persistence
The DT records secure firmware interface registers. Runtime state is held by secure firmware and kernel firmware-call glue.

## Dependencies And Integration Points
It integrates with Samsung/Exynos firmware interfaces and any platform code that uses secure services.

## Risks
Incorrect MMIO region can break secure calls or map unrelated registers. The strict schema requires updates before adding new firmware properties.

## Test Signals
`dtbs_check` validates the node. Runtime signals include successful secure firmware probe and secure-service calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-secure-firmware.yaml -->
