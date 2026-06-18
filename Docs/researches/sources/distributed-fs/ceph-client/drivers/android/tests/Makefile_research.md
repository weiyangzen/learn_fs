# sources/distributed-fs/ceph-client/drivers/android/tests/Makefile

## Purpose
This Makefile wires the Android Binder allocator KUnit test object into the kernel build.

## Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_ANDROID_BINDER_ALLOC_KUNIT_TEST) += binder_alloc_kunit.o`. There are no functions or runtime types.

## Control Flow
Kbuild includes `binder_alloc_kunit.o` only when `CONFIG_ANDROID_BINDER_ALLOC_KUNIT_TEST` is enabled. Otherwise the tests are absent from the build.

## State And Persistence
No runtime state exists. The file controls build graph membership.

## Dependencies
It depends on Kbuild, the config symbol `ANDROID_BINDER_ALLOC_KUNIT_TEST`, and the adjacent `binder_alloc_kunit.c` source.

## Integration Points
The rule integrates Binder allocator tests with the kernel KUnit build and module/test discovery. It is the entry point for building the exhaustive allocator page-LRU tests.

## Risks
If the config symbol changes or the object name drifts, allocator tests silently stop building. The Makefile does not list additional objects, so all required test imports must come from exported Binder symbols and normal kernel links.

## Test Signals
Enable `CONFIG_ANDROID_BINDER_ALLOC_KUNIT_TEST`, run the KUnit suite named `binder_alloc`, and verify `binder_alloc_kunit.o` appears in the build output.
