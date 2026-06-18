# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/Makefile

## Purpose

This Makefile descends into the three Amlogic C3 media component directories.

## Important APIs, Types, And Symbols

- `obj-y += isp/`
- `obj-y += mipi-adapter/`
- `obj-y += mipi-csi2/`

## Control Flow

Kbuild traverses each child directory and lets each child Makefile apply `CONFIG_*` gates to actual objects.

## State And Persistence

No runtime state exists here. Build state is produced by child objects.

## Dependencies And Integration Points

The traversal mirrors `amlogic/c3/Kconfig`, keeping the ISP, MIPI adapter, and CSI-2 components build-reachable.

## Risks

Pipeline components can become impossible to build if Kconfig and Makefile child lists diverge. Since the entries are unconditional traversal, stale child directories can surface build issues in broad configs.

## Test Signals

Allmodconfig and targeted `CONFIG_VIDEO_C3_ISP` builds should traverse `isp/` successfully.
