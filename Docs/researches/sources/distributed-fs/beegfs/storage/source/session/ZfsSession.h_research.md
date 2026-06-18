<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/ZfsSession.h -->
## sources/distributed-fs/beegfs/storage/source/session/ZfsSession.h

### Purpose
Declares the ZFS quota query session wrapper and cached ZFS pool handle map.

### Important APIs, Types, And Functions
Public APIs include constructor/destructor, initZfsSession(), getZfsDeviceHandle(), function pointers used by QuotaTk, getlibZfsHandle(), and isSessionValid().

### Control Flow
The class is a thin ABI bridge around libzfs loaded at runtime rather than linked directly.

### State, Persistence, And Dependencies
State includes dlOpenHandleLibZfs, libZfsHandle, fsHandles, zfs_open pointer, quota/error function pointers, and isValid. Depends on std::map types, target IDs, and libzfs-compatible opaque void* handles.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include public mutable function pointer members and raw void* handles with no type safety.

### Test Signals
Test signals include initialization state transitions and caller checks of isSessionValid before ZFS requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/ZfsSession.h -->
