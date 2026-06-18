# sources/distributed-fs/ceph-client/include/linux/soc/apple/sart.h

Purpose: This header exposes Apple SART access-control management for devices that need to allow or revoke DMA-visible physical memory regions through Apple system address range tables.

Important APIs/types/functions: It declares opaque `struct apple_sart`, `devm_apple_sart_get`, `apple_sart_add_allowed_region`, and `apple_sart_remove_allowed_region`. Regions are expressed as physical address and size.

Control flow: A consumer gets the SART provider for its device, adds allowed regions before firmware/device DMA access, and removes them when buffers are no longer valid.

State and persistence: SART hardware stores access-control entries. The provider likely tracks slot allocation and region ownership; entries persist until removed or hardware reset.

Dependencies and integration: Uses `struct device` and `phys_addr_t`. Integrates with Apple DMA-capable coprocessor drivers, RTKit clients, and platform security/IO mapping code.

Risks and test signals: Failure to add entries blocks device DMA; failure to remove entries leaves stale DMA access to memory. Overlapping or incorrectly sized regions can violate isolation. Test DMA success/failure around add/remove, cleanup on probe errors, suspend/resume, and teardown ordering.
