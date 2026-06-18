# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/note.S

## Purpose
Adds ELF note sections to the PowerPC vDSO, including kernel version and build salt metadata.

## Important APIs, Types, And Functions
Defines `ASM_ELF_NOTE_BEGIN` and `ASM_ELF_NOTE_END` macros, emits `.note.kernel-version` with `LINUX_VERSION_CODE`, and includes `BUILD_SALT`.

## Control Flow
At assembly time the macros lay out a standard ELF note with aligned name, descriptor, and type fields. The linker scripts collect `.note.*` into a PT_NOTE segment.

## State And Persistence
The resulting metadata is embedded read-only in the vDSO ELF image and visible to userspace ELF readers.

## Dependencies And Integration Points
Depends on Linux version headers, build-salt support, and vDSO linker scripts that map `.note` into a read-only note program header.

## Risks And Edge Cases
Alignment and length fields must match ELF note format. Incorrect note layout can confuse tooling that inspects vDSO metadata.

## Test Signals
Use `readelf -n` on built `vdso32.so.dbg` and `vdso64.so.dbg` to verify kernel-version and build-salt notes parse correctly.
