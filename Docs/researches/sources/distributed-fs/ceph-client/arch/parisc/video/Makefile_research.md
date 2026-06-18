# sources/distributed-fs/ceph-client/arch/parisc/video/Makefile

## Purpose
Minimal PA-RISC video build glue. It adds `video-sti.o` to the architecture video objects when `CONFIG_STI_CORE` is enabled.

## Important APIs, Types, And Control Flow
There are no functions or runtime control paths. The single object rule `obj-$(CONFIG_STI_CORE) += video-sti.o` binds PA-RISC STI firmware framebuffer integration to the STI core Kconfig symbol.

## State, Dependencies, Risks, And Tests
State is build-system selection only. Dependencies are kbuild and `CONFIG_STI_CORE`. Risks are accidental omission of `video-sti.o` from STI-enabled kernels or unwanted inclusion when STI is disabled. Test signals are PA-RISC builds with `CONFIG_STI_CORE=y/m/n` and symbol availability for `video_is_primary_device`.
