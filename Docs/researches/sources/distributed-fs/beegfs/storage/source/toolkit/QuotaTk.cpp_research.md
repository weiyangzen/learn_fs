<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.cpp -->
## sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.cpp

### Purpose
Implements quota usage retrieval across ext-family, XFS, and ZFS storage target block devices.

### Important APIs, Types, And Functions
Important functions are appendQuotaForID(), requestQuotaForRange(), requestQuotaForList(), checkQuota(), initLibZfs(), uninitLibZfs(), checkRequiredLibZfsFunctions(), and requestQuotaFromZFS().

### Control Flow
Range/list helpers repeatedly call appendQuotaForID(). checkQuota() iterates QuotaBlockDeviceMap and dispatches to XFS Q_XGETQUOTA, ZFS property reads, or generic Q_GETQUOTA, merges block and inode counters into QuotaData, and tolerates missing-user ESRCH/XFS ENOENT. ZFS support dynamically loads libzfs functions and probes inode quota support, falling back to ZFSOLD when needed.

### State, Persistence, And Dependencies
No BeeGFS persistent state is written. Runtime state includes ZfsSession handles, App libzfs error-reported flag, and returned QuotaData counters. Kernel quota subsystem state is read through quotactl. Depends on QuotaData, QuotaBlockDevice, ZfsSession, Program/App, UnitTk, System logging, boost lexical_cast, dlfcn, quotactl, xfs headers, and ZFS user/group property names.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include large ID ranges causing many syscalls, ZFS property names built from IDs without validation, mixed-target partial failures returning false while preserving some data, dynamic libzfs ABI drift, and fstype UNKNOWN falling into generic quotactl path.

### Test Signals
Test signals include ext/XFS/ZFS quota reads, missing users, invalid quota type, partial target failure, ZFSOLD inode behavior, missing libzfs symbols, and counter merging across multiple block devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.cpp -->
