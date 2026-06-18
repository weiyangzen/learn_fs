<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.c

## Purpose
Implements the IBM Z `zipl` bootloader backend, including deferred zipl execution, secure boot detection, and Secure Execution image generation on s390x.

## Important APIs and Types
`OstreeBootloaderZipl` stores an `OstreeSysroot*`. The backend query is architecture-dependent, write creates `boot/ostree-bootloader-update.stamp`, and post-BLS sync invokes either Secure Execution handling or standard `zipl`. Secure Execution helpers mount `/dev/disk/by-label/se`, find host keys, copy/augment initrd with LUKS material through libarchive, run `genprotimg`, and call `zipl` on the generated secure image.

## Control Flow
Query returns active on `__s390x__` only. Post-sync skips unprivileged contexts and no-stamp cases, chooses a target deployment for containerized execution when not booted, checks Secure Execution sysfs, runs the SE flow if enabled, otherwise detects Secure Boot through sysfs or `/dev/kmsg`, runs `zipl --secure 1|auto -V` either in the deployment via bubblewrap helper or directly, checks exit status, and removes the stamp.

## State and Persistence
Persistent state includes the update stamp, generated secure boot image under `/sysroot/se/sdboot`, and external bootloader state written by `zipl`. The Secure Execution path temporarily mounts and unmounts the SE partition and writes anonymous temporary initrd/cmdline files.

## Dependencies and Integration Points
Depends on sysroot/deployment private APIs, libarchive on s390x, GIO Unix input streams, sysfs, `/dev/kmsg`, `genprotimg`, `zipl`, host key files, LUKS key/config paths, and the shared bootloader interface.

## Risks
The SE enable path chains operations with `&&`; if an intermediate step fails after mount, unmount may be skipped. Reading `/dev/kmsg` assumes lines are available and does not visibly handle NULL lines before `strstr`. The backend touches sensitive LUKS material and depends on privileged host execution.

## Test Signals
Tests should cover stamp lifecycle, unprivileged no-op, s390x vs non-s390x query, Secure Boot sysfs and kmsg fallbacks, SE key discovery, missing LUKS material, `genprotimg`/`zipl` failures, and deployment-contained execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.c -->
