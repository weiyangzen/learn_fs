# File Research: sources/block-storage/lvm2/tools/vgchange.c

Purpose: implements `vgchange` and its specialized subcommands for VG property changes, LV activation/deactivation, monitoring/polling, lock manager start/stop/type conversion, system ID changes, persistent reservation operations, and lock-argument updates.

Read coverage: complete file read, 2,019 lines.

Key responsibilities:
- Activates/deactivates visible LVs in a VG, respecting activation-skip, autoactivation filters, VG/LV no-autoactivate flags, incomplete VG policy, foreign VG restrictions, and open LV checks.
- Starts background polling for active pvmove/conversion/merge LVs and registers/unregisters dmeventd monitoring.
- Implements mutable VG property changes: max LVs/PVs, resizeable flag, autoactivation flag, tags, PE size, UUID, allocation policy, metadata copies, and metadata/profile attachment.
- Changes VG system ID with prompts when making a VG foreign or removing ownership, optional majority-PV requirement, and optional PR start/stop coupling.
- Implements autoactivation setup optimized around `/run/lvm` online PV state, early VG locking, one-scan processing, and root-VG system.devices bootstrap trigger.
- Implements `--locktype` conversion among `none`, `clvm`, and lockd types, including forced recovery mode, sanlock staged LV lock allocation, lockd cleanup, and PR key preservation.
- Implements `--lockstart`/`--lockstop`, including config filters, auto/nowait behavior, sanlock wait messaging, and optional PR coordination.
- Implements PR commands: check, read, start, stop, remove, clear, autostart, plus `--setpersist` metadata changes and validation of local PR config and root VG restrictions.
- Implements `--setlockargs`, delegating lockspace/PR-safe mutation to lockd and writing updated metadata.

Dependencies:
- Uses activation, dmeventd monitor APIs, polling, metadata mutation helpers, device-id updates, persistent reservation helpers, lvmlockd, system.devices/hints, online PV scanning, command processing framework, and config tree accessors.

Risks and edge cases:
- Activation paths deliberately allow deactivation of active foreign VGs but reject foreign activation.
- `vgchange -aay --autoactivation event` has a fast path that must fall back cleanly if online PV state is missing or incomplete.
- PR operations intentionally bypass or disable normal lock requirements in some modes because PR may be needed before shared locking can operate.
- Lock type changes have multi-step side effects, especially sanlock, where VG and LV lock args cannot all be valid until after the lvmlock LV exists.
- UUID changes must also update device IDs for PVs stacked on LVs when LV scanning is enabled.
