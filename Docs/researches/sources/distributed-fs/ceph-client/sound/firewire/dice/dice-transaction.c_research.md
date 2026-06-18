# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-transaction.c

Purpose: provides DICE register transaction helpers, clock/rate reads, global enable control, notification callback registration, owner compare-swap, and subaddress discovery.

Important APIs/functions: `snd_dice_transaction_write`, `snd_dice_transaction_read`, `snd_dice_transaction_get_clock_source`, `snd_dice_transaction_get_rate`, `snd_dice_transaction_set_enable`, `snd_dice_transaction_clear_enable`, `snd_dice_transaction_init`, `snd_dice_transaction_reinit`, and `snd_dice_transaction_destroy`. Internal functions include `get_subaddr`, `dice_notification`, `register_notification_address`, `unregister_notification_address`, and `get_subaddrs`.

Control flow and state: init validates section offsets/sizes, checks DICE major version when available, registers a host address handler, and claims `GLOBAL_OWNER` by compare-swap. Notifications OR bits into `dice->notification_bits`, complete `clock_accepted` when appropriate, and wake hwdep. Enable writes are generation-fixed and update `global_enabled`. Destroy unregisters owner and address handler.

Dependencies/integration: uses FireWire transactions/address handlers, DICE register macros, hwdep wait queue, stream clock selection, and bus-reset reinit. Risks include owner races with other hosts, old firmware without capability registers, retry logic around `-EAGAIN`, notification bit coalescing, and generation mismatch. Test signals are successful probe owner claim, hwdep notification reads, clock accepted completion, and re-registration after bus reset.
