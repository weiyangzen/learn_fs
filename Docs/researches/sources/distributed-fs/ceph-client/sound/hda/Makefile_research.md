# sources/distributed-fs/ceph-client/sound/hda/Makefile

## Purpose

This Makefile defines top-level HDA build ordering across core, common, codecs, and controllers.

## Important APIs, types, and functions

`obj-y += core/` always descends into the core directory. `obj-$(CONFIG_SND_HDA) += common/ codecs/ controllers/` conditionally builds the remaining HDA pieces. A comment documents that controllers must be listed last so built-in codec drivers hook before PCI probe.

## Control flow

Kbuild descends into directories in the listed order. When `CONFIG_SND_HDA` is disabled only `core/` is traversed; when enabled, common and codec drivers are built before controllers.

## State and persistence behavior

No runtime state exists. The file controls build-time object ordering, which affects built-in initialization behavior.

## Dependencies and integration points

It must match Kconfig symbols and directory layout. The controller ordering integrates with codec driver registration expectations.

## Risks and test signals

Risks include reordering controllers before codecs, causing built-in probe ordering regressions, or missing directories from the build. Test signals are built-in HDA boots, module builds, and link/order checks after Makefile edits.
