<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.h -->
## sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.h

### Purpose
Declares QuotaBlockDevice, the value object that records the mount, device path, filesystem type, and normalized storage target path used for quota backends.

### Important APIs, Types, And Functions
Public APIs include default and value constructors, static discovery helpers, quotaInodeSupportFromBlockDevice(), getFsType(), getters/setters, and supportsInodeQuota(). It also defines QuotaBlockDeviceMap typedefs.

### Control Flow
The class abstracts filesystem-specific quota capability decisions away from quota message handlers and QuotaTk.

### State, Persistence, And Dependencies
State is storageTargetPath, mountPath, blockDevicePath, and fsType. It is copied into maps for quota query requests. Depends on Common.h, Path, StorageDefinitions, and quota enums.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include mutable setters allowing fsType/path changes after discovery and UNKNOWN default values that callers must handle.

### Test Signals
Test signals include constructor normalization, supportsInodeQuota for EXTX/XFS/ZFS/ZFSOLD/UNKNOWN, and map usage by target ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.h -->
