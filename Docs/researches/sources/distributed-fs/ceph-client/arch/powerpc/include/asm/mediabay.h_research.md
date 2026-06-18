# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mediabay.h

Purpose: defines media-bay content constants and PMAC media-bay helper APIs used by PowerBook-style removable bays.

Important APIs/types/functions: content states include `MB_FD`, `MB_FD1`, `MB_SOUND`, `MB_CD`, `MB_PCI`, `MB_POWER`, and `MB_NO`. With `CONFIG_PMAC_MEDIABAY`, it declares `check_media_bay`, `lock_media_bay`, and `unlock_media_bay`; otherwise stubs return `MB_NO` or no-op.

Control flow: drivers query bay contents and lock callbacks while initializing ATA or other bay devices. Disabled builds treat the bay as empty.

State and persistence: bay state is maintained by the media-bay implementation and hardware; this header stores none.

Dependencies and integration points: forward-declares `struct macio_dev` and integrates PMAC MacIO devices with media-bay hotplug/control code.

Risks: callers must handle transition states as `MB_NO`. Forgetting to unlock bay callbacks can block hotplug notifications. Stubs make unsupported configurations silently behave as no device.

Test signals: hot-swap media-bay devices on supported PowerBooks, verify ATA initialization lock/unlock behavior, transition handling, and no-op behavior with PMAC media bay disabled.
