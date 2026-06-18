<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mvebu-icu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mvebu-icu.h

## Purpose
This header defines Marvell MVEBU ICU interrupt group IDs for device-tree interrupt specifiers.

## Important APIs, types, and functions
It exports four group constants: `ICU_GRP_NSR`, `ICU_GRP_SR`, `ICU_GRP_SEI`, and `ICU_GRP_REI`.

## Control flow
DTS nodes use these values in the first interrupt specifier cell. The MVEBU ICU driver decodes the group and maps it to the correct interrupt parent/routing class.

## State and persistence
No state is present. The constants are stable DT binding values.

## Dependencies and integration points
It integrates with Marvell ICU irqchip code, parent interrupt controllers, and Armada/MVEBU platform device interrupt declarations.

## Risks and test signals
Risks include choosing the wrong security or error-interrupt group and mismatching device-tree group IDs with firmware routing. Test signals include `dtbs_check`, ICU probe, interrupt delivery for NSR/SR events, and platform-specific error interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mvebu-icu.h -->
