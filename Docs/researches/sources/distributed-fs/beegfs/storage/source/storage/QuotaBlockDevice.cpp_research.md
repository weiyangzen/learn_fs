<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.cpp -->
## sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.cpp

### Purpose
Discovers and classifies the filesystem/block device backing storage targets for quota queries.

### Important APIs, Types, And Functions
APIs are getBlockDeviceOfTarget(), getBlockDevicesOfTargets(), quotaInodeSupportFromBlockDevice(), and getFsType(). getFsType() maps statfs magic values to EXTX, XFS, ZFS, or UNKNOWN.

### Control Flow
getBlockDeviceOfTarget() uses StorageTk::findMountForPath(), constructs a normalized QuotaBlockDevice from mount path, device, fs type, and storage target path, then checks libzfs compatibility for ZFS targets when needed. Multi-target discovery iterates target path maps.

### State, Persistence, And Dependencies
Persistent state is not changed. Runtime state is the returned QuotaBlockDevice values and possible App libzfs error/support flags set through QuotaTk during ZFS probing. Depends on StorageTk mount lookup, Program/App, QuotaTk, statfs filesystem magic constants, Path normalization, and Linux filesystem headers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include throwing runtime_error from getFsType() on statfs failure, hard-coded ZFS magic, and returning a default UNKNOWN block device when no mount is found without an explicit error.

### Test Signals
Test signals include ext4/XFS/ZFS/unknown statfs mappings, no mount found, normalized storage paths, ZFSOLD fallback via QuotaTk, and multi-target map population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.cpp -->
