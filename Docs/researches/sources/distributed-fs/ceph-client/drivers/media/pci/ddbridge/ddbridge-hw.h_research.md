# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-hw.h

Purpose: exposes the ddbridge hardware metadata lookup interface. It defines the Digital Devices vendor ID and `struct ddb_device_id`.

Important APIs/types/functions: `DDVID` is `0xdd01`. `struct ddb_device_id` stores PCI vendor/device/subvendor/subdevice plus a pointer to `struct ddb_info`. `get_ddb_info()` resolves PCI IDs to immutable board info.

Control flow: included by `ddbridge-main.c` for probe-time board lookup and by `ddbridge-hw.c` for implementation.

State and persistence: no mutable state; this header only declares metadata shape and lookup API.

Dependencies/integration: includes `ddbridge.h` for `struct ddb_info`.

Risks and test signals: API changes affect PCI probing. Compile coverage plus probe of known supported PCI IDs are the main signals.
