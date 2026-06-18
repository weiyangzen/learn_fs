## sources/distributed-fs/ceph-client/arch/arm/vdso/note.c

### Purpose
Adds ELF note metadata and build salt to the ARM vDSO image.

### Important APIs, Types, And Functions
Uses `ELFNOTE32("Linux", 0, LINUX_VERSION_CODE)` and `BUILD_SALT`.

### Control Flow
There is no runtime logic. The compiler emits note sections that the vDSO linker script places into the PT_NOTE segment.

### State, Persistence, And Dependencies
Persistent state is embedded ELF note data. Dependencies include `linux/version.h`, `linux/elfnote.h`, and `linux/build-salt.h`.

### Integration Points
The note is linked with vDSO text and visible to userspace ELF tooling and debuggers.

### Risks
Incorrect note section format can break vDSO validation or confuse consumers that inspect vDSO metadata.

### Test Signals
Run `readelf -n` on `vdso.so.dbg` and confirm Linux version and build salt notes are present.
