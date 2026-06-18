<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.h -->
## sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.h

### Purpose
Declares static quota toolkit functions for querying usage and managing dynamic ZFS support.

### Important APIs, Types, And Functions
The QuotaTk class exposes ID, range, and list quota request helpers; checkQuota(); init/uninit libzfs; checkRequiredLibZfsFunctions(); and requestQuotaFromZFS(). Constructor is private.

### Control Flow
The header centralizes backend quota APIs so message handlers do not directly call quotactl or libzfs.

### State, Persistence, And Dependencies
No state is held by the class; state is passed through QuotaBlockDeviceMap, QuotaData, and ZfsSession parameters. Depends on Common.h, QuotaData, ZfsSession, and QuotaBlockDevice.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include raw pointer parameters and no explicit ownership annotations; callers must pass valid output lists and sessions.

### Test Signals
Test signals include compile coverage for all backend function declarations and null/invalid pointer behavior through cpp tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.h -->
