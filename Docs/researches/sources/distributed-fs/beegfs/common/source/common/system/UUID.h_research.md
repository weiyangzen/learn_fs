<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/UUID.h -->
## sources/distributed-fs/beegfs/common/source/common/system/UUID.h

Purpose: Provides header-only UUID helpers without forcing all common-library users to link libblkid.

Important APIs/functions: `UUID::getFsUUID` resolves the device for a mountpoint and probes its filesystem UUID. `UUID::getPartUUID` scans blkid cache entries for a preferred mountpoint UUID/PARTUUID with fallback rules. `UUID::getMachineUUID` reads `/sys/class/dmi/id/product_uuid` and falls back to partition UUID.

Control flow/state/persistence: Functions query system files/devices and blkid cache; they do not persist state. `getFsUUID` throws `InvalidConfigException`; `getPartUUID` returns `FhgfsOpsErr` plus text; `getMachineUUID` logs warnings and returns empty string on failure.

Dependencies/integration: Uses `System::getDevicePathFromMountpoint`, libblkid, `StorageErrors`, and logging. Used by service startup/storage identity checks.

Risks/test signals: Requires device permissions for full probing, and cache order influences fallback identity. Tests should cover inaccessible devices, missing DMI UUID, non-36-character UUIDs, preferred mountpoint selection, and blkid cache failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/UUID.h -->
