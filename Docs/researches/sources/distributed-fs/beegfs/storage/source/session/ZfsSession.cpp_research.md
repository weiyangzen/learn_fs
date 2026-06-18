<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/ZfsSession.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/ZfsSession.cpp

### Purpose
Implements dynamic libzfs session management for quota queries against ZFS-backed storage targets.

### Important APIs, Types, And Functions
APIs are constructor, destructor, initZfsSession(void*), and getZfsDeviceHandle(uint16_t, string). It loads function pointers zfs_open, zfs_prop_get_userquota_int, libzfs_error_description, and libzfs_error_action.

### Control Flow
The constructor creates an invalid session. initZfsSession() stores the dlopen handle, calls QuotaTk::initLibZfs(), resolves required symbols through dlsym(), marks App libzfs error state on failures, and returns validity. getZfsDeviceHandle() reuses a cached per-target handle or opens a new ZFS filesystem/pool handle.

### State, Persistence, And Dependencies
Runtime state is the libzfs handle, dlopen handle, function pointers, validity flag, and fsHandles map. The destructor calls QuotaTk::uninitLibZfs(); individual zfs handles are cached but not explicitly closed in this file. Depends on QuotaTk, Program/App error reporting, dlfcn, libzfs ABI names, and ZFSSESSION_ZFS_TYPE matching libzfs ZFS_TYPE_FILESYSTEM.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include ABI drift in libzfs symbols/signatures, not clearing dlerror before each dlsym, cached zfs_open handles lacking explicit close, and a single invalid symbol leaving partial state in the object.

### Test Signals
Test signals include missing dlopen handle, missing symbols, invalid libzfs init, handle reuse per target, ZFS error logging, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/ZfsSession.cpp -->
