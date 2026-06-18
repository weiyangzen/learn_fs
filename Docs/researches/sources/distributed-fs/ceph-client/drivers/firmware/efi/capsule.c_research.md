# sources/distributed-fs/ceph-client/drivers/firmware/efi/capsule.c

Purpose: provides the kernel EFI capsule submission core: validation with `QueryCapsuleCapabilities()`, scatter-gather block descriptor construction, serialized `UpdateCapsule()` calls, and pending-reset state tracking.

Important APIs/types/functions: exports `efi_capsule_supported()` and `efi_capsule_update()`. Internal state is `capsule_pending`, `stop_capsules`, `efi_reset_type`, and `capsule_mutex`; helpers include `efi_capsule_pending()`, `sg_pages_num()`, `efi_capsule_update_locked()`, and reboot notifier registration.

Control flow: callers validate a capsule by GUID, flags, and size. Supported flags are restricted to persist-across-reset and populate-system-table. `efi_capsule_update()` revalidates support, allocates pages for EFI block descriptor lists, fills descriptors that reference the caller's capsule data pages, adds continuation pointers, flushes cache on ARM/ARM64, then calls `efi.update_capsule()` under `capsule_mutex`. On success it marks a capsule pending and records the reset type. A reboot notifier sets `stop_capsules` so capsule updates cannot race with reset handling.

State and persistence behavior: pending capsule state is in-memory and protected by `capsule_mutex`. Capsule data pages remain caller-owned and must not be freed after successful submission. SG-list pages are retained on success because firmware may need them; they are freed only on failed submission.

Dependencies and integration points: depends on EFI runtime function pointers, architecture cache maintenance, reboot notifier chain, and the loader/device or other kernel capsule submitters.

Risks and test signals: reset-type conflicts, reboot races, unsupported flags, firmware maximum-size limits, and SG-list page lifetime are the main hazards. Test signals include `efi_capsule_supported()` returning expected errors, `efi_capsule_pending()` reporting reset type after update, and reboot paths observing pending capsules without racing new submissions.
