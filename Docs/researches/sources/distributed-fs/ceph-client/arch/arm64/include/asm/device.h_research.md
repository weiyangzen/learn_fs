## sources/distributed-fs/ceph-client/arch/arm64/include/asm/device.h

Purpose: provides arm64 architecture-private device state slots.

Important APIs/types/functions: defines `struct dev_archdata` and `struct pdev_archdata` as currently empty/placeholder architecture data containers.

Control flow: none.

State and persistence: device core embeds these structures in device/platform-device objects, reserving architecture extension space.

Dependencies and integration: included by generic device structures and platform bus code.

Risks: adding fields affects device lifetime and initialization expectations. Test signals are allmodconfig builds and device probe/remove tests.
