# sources/distributed-fs/ceph-client/drivers/md/Makefile

## Purpose
The Makefile composes software RAID, bcache, and device-mapper objects for Kbuild.

## Important APIs, Types, and Functions
It defines object groups for `dm-mod`, multipath path selectors, snapshots, mirrors, thin/cache metadata targets, `md-mod`, `raid456`, `linear`, and many individual DM targets. It also descends into `bcache/`, `persistent-data/`, `dm-vdo/`, and `dm-pcache/` based on config symbols.

## Control Flow, State, and Persistence
There is no runtime flow. Build ordering matters: RAID personalities are linked before `md.o` so personality init is available for MD auto-initialization. Conditional `dm-mod-objs` additions include init, uevent, zone, IMA, audit, and verity helper objects.

## Dependencies and Integration Points
This file is the Kbuild integration point for `drivers/md/Kconfig` symbols and module names. It ties MD, bcache, and DM code to block-layer kernel builds.

## Risks and Test Signals
Risks include link-order regressions, config/object mismatches, built-in-only helpers being omitted, and optional feature objects not following Kconfig dependencies. Tests should include `make drivers/md/` under representative configs, module installs, and `modpost` validation for enabled DM features.
