<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/Makefile

## Purpose
Builds the minimal decompression library used by Xtensa compressed boot images.

## Important APIs, Types, And Functions
Key variables are `zlib := inffast.c inflate.c inftrees.c`, `lib-y`, `ccflags-y`, instrumentation disable flags, stack-protector removal flags, and `cmd_copy_zlib`.

## Control Flow
Kbuild copies selected zlib inflate sources from `lib/zlib_inflate`, builds them plus `zmem.o` into `arch/xtensa/boot/lib/lib.a`, removes function tracing and sanitizers, and disables stack protector for these early-boot objects.

## State And Persistence
Build output is a boot-only static archive and copied zlib source files in the object tree.

## Dependencies And Integration Points
Depends on generic zlib inflate sources, `zmem.c`, the boot-redboot linker, and early boot constraints where normal kernel instrumentation is unavailable.

## Risks And Edge Cases
Instrumentation or stack protector would introduce unavailable runtime dependencies. Zlib source copy rules must track upstream filenames. The library assumes the boot loader supplies heap bounds.

## Test Signals
Build `zImage`, inspect that sanitizer/ftrace/stack-protector instrumentation is absent, and boot a compressed image through decompression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/Makefile -->
