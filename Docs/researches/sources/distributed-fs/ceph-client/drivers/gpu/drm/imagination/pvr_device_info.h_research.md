# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device_info.h

Purpose: defines PowerVR hardware feature, quirk, and enhancement state structures plus mapping APIs.

Important APIs/types: `struct pvr_device_features` contains `has_*` booleans and value fields for firmware-advertised capabilities. `struct pvr_device_quirks` and `struct pvr_device_enhancements` contain supported BRN/ERN booleans. Setters are `pvr_device_info_set_quirks()`, `pvr_device_info_set_enhancements()`, and `pvr_device_info_set_features()`. The header also defines META core constants and public `PVR_FEATURE_*` identifiers for UAPI/derived feature lookup.

Control flow and state: instances live inside `struct pvr_device` and are populated during firmware validation/device init.

Dependencies and integration: forward declares `pvr_device`; implementation depends on firmware ABI bit indices. Device, stream, query, and job code use the feature/quirk values.

Risks: adding a firmware feature requires updating the struct, mapping table, and any public derived feature IDs. Boolean presence and value fields must be interpreted together.

Test signals: firmware load on known GPUs should set expected fields; device-query ioctls should report filtered public features consistently.
