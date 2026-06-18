# sources/distributed-fs/ceph-client/include/dt-bindings/arm/mhuv3-dt.h

Purpose: defines device-tree constants for ARM MHUv3 extension channel types.

Important APIs/types/functions: `DBE_EXT`, `FCE_EXT`, and `FE_EXT` assign numeric IDs for the defined MHUv3 extension classes.

Control flow: DTS bindings use these constants in MHUv3 channel/type cells; the driver interprets them when instantiating mailbox resources.

State and persistence: constants are stable DT ABI values.

Dependencies and integration: standalone DT binding used by ARM mailbox/MHUv3 device trees and drivers.

Risks and test signals: incorrect IDs break mailbox channel discovery. Test dt-schema examples and MHUv3 probe using each extension type.
