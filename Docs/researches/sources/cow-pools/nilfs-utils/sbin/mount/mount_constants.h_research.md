# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_constants.h

## Scope

Provides fallback mount flag definitions for legacy mount helper code.

## API Surface

Defines Linux `MS_*` constants when missing, including read-only, nosuid, nodev, noexec, synchronous, remount, dirsync, noatime, nodiratime, bind, move, recursive, relatime, and magic mask/value flags.

## Dependencies And Risks

This compatibility header allows older libc/kernel headers. Values must match Linux mount ABI; incorrect fallback values would corrupt `mount(2)` flag behavior.
