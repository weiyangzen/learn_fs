# sources/distributed-fs/ceph-client/include/dt-bindings/ata/ahci.h

Purpose: exposes AHCI device-tree capability bit constants for generic HBA and port properties.

Important APIs/types/functions: HBA capability bits include `HBA_SSS` and `HBA_SMPS`. Port capability bits include hot-plug capable, mechanical presence switch, cold presence detect, external SATA port, and FIS-based switching capable.

Control flow: DTS properties use these bit values; AHCI platform drivers read the properties and set or override hardware capability fields.

State and persistence: constants are DT ABI; runtime state is in driver capability masks.

Dependencies and integration: standalone binding for AHCI platform DT nodes and libahci/platform drivers.

Risks and test signals: wrong bit positions enable or disable SATA features incorrectly. Test DT schema, platform probe capability masks, hotplug, staggered spin-up, and external/FBS behavior.
