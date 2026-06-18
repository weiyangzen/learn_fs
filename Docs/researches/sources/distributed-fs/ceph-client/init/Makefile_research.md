# sources/distributed-fs/ceph-client/init/Makefile

## Purpose
`init/Makefile` controls compilation of early kernel initialization objects, mount/initramfs support, delay calibration, init task, initramfs tests, and generated UTS version headers.

## Important APIs, Types, and Functions
Important build variables include `obj-y`, `obj-$(CONFIG_BLK_DEV_INITRD)`, `obj-$(CONFIG_GENERIC_CALIBRATE_DELAY)`, `mounts-y`, `mounts-$(CONFIG_BLK_DEV_RAM)`, `mounts-$(CONFIG_BLK_DEV_INITRD)`, `smp-flag-*`, `preempt-flag-*`, `build-version`, `build-timestamp`, and `filechk_uts_version`. It generates `utsversion-tmp.h` and `include/generated/utsversion.h`.

## Control Flow
Kbuild compiles `main.o`, `version.o`, `mounts.o`, optional `initramfs.o` or `noinitramfs.o`, optional `calibrate.o`, optional `initramfs_test.o`, and `init_task.o`. The `mounts.o` composite pulls in root-mount helpers according to block RAM/initrd config. Version object builds include generated UTS headers with temporary or final timestamps.

## State and Persistence Behavior
Generated UTS version headers persist in the build tree and encode build version, SMP/preempt flags, and timestamp truncated to 64 bytes. Clean rules remove `utsversion-tmp.h`.

## Dependencies and Integration Points
It integrates Kconfig options with early init source compilation and Kbuild `filechk`. It depends on `scripts/build-version`, `date`, generated headers, and object composition conventions.

## Risks and Test Signals
Risks include non-reproducible timestamps, UTS version truncation, mismatched initrd/noinitramfs object selection, and missing mount composite members. Test signals include builds with and without `BLK_DEV_INITRD`, `BLK_DEV_RAM`, `GENERIC_CALIBRATE_DELAY`, `INITRAMFS_TEST`, SMP/preempt variants, and reproducible build environment variables.
