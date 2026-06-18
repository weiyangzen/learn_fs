# sources/distributed-fs/ceph-client/drivers/media/test-drivers/Makefile

Purpose: build dispatcher for media test drivers.

Important APIs/types/functions: maps config symbols to objects/subdirectories: `CONFIG_DVB_VIDTV` to `vidtv/`, `CONFIG_VIDEO_VICODEC` to `vicodec/`, and other virtual V4L drivers to their objects/directories.

Control flow: Kbuild descends into subdirectories or builds objects when each config symbol is enabled. The file notes entries should remain alphabetically sorted by Kconfig name.

State and persistence: no runtime state; it is Kbuild metadata.

Dependencies and integration points: integrates with the top-level media driver build and child Makefiles for `vidtv` and `vicodec`.

Risks: symbol/object mismatches silently drop a driver from builds. Ordering is cosmetic but helps maintainability.

Test signals: compile with each affected config as `m` and `y`, and check generated modules include `vicodec.ko`, `dvb-vidtv-bridge.ko`, `dvb-vidtv-demod.ko`, and `dvb-vidtv-tuner.ko` as appropriate.
