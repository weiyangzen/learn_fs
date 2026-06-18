# sources/distributed-fs/ceph-client/drivers/pmdomain/apple/Makefile

Purpose: Kbuild mapping for Apple PMGR PM-domain support.

Important APIs/types/functions: builds `pmgr-pwrstate.o` when `CONFIG_APPLE_PMGR_PWRSTATE` is enabled.

Control flow: no runtime flow.

State and persistence: build output follows `.config`.

Dependencies/integration: synchronized with `apple/Kconfig`.

Risks: stale object name would make the Kconfig option ineffective.

Test signals: targeted build with `CONFIG_APPLE_PMGR_PWRSTATE=y`.
