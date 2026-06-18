# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-hwdep.c

Purpose: exposes the DICE ALSA hwdep interface for node info, stream lock state, userspace locking, and DICE notification events.

Important APIs/functions: `hwdep_read`, `hwdep_poll`, `hwdep_get_info`, `hwdep_lock`, `hwdep_unlock`, `hwdep_release`, `hwdep_ioctl`, optional compat ioctl, and `snd_dice_create_hwdep`.

Control flow and state: read waits until either `dev_lock_changed` or `notification_bits` is set, then returns a lock-status event or `SNDRV_FIREWIRE_EVENT_DICE_NOTIFICATION` and clears the consumed flag. Ioctls expose FireWire card/GUID/name info and set/clear userspace lock ownership. State is spinlock-protected.

Dependencies/integration: receives notification bits from `dice-transaction.c`, coordinates with PCM/MIDI stream locks, and uses ALSA hwdep/UAPI. Risks include lost notifications if bits coalesce, userspace lock contention, and read starvation if both lock and notification events alternate. Test signals are poll readiness on device notifications, lock ioctl behavior, and correct `GET_INFO` metadata.
