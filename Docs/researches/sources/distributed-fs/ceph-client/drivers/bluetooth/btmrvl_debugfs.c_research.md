# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_debugfs.c

## Purpose
Provides debugfs controls and status files for the Marvell Bluetooth driver. It exposes runtime knobs for power-save mode, power-save command trigger, host-sleep mode, host-sleep command trigger, host-sleep GPIO/gap configuration, and host-sleep configuration command trigger, plus read-only status for current power-save and host-sleep state.

## Important APIs, Types, And Functions
- `struct btmrvl_debugfs_data` stores the created `config` and `status` directory dentries.
- Write/read handlers `btmrvl_hscfgcmd_write/read`, `btmrvl_pscmd_write/read`, and `btmrvl_hscmd_write/read` bridge debugfs integer writes to fields in `priv->btmrvl_dev`.
- File-operation tables connect those handlers through `simple_open` and `default_llseek`.
- `btmrvl_debugfs_init` creates debugfs directories/files under `hdev->debugfs`.
- `btmrvl_debugfs_remove` removes both directories recursively and frees the stored debugfs data.

## Control Flow
Initialization runs after HCI registration if debugfs is enabled and `hdev->debugfs` exists. It allocates a small tracking object, creates `config` files backed directly by `btmrvl_dev` fields, and creates `status` files backed by `adapter` state fields. Writing a nonzero trigger file updates the corresponding command flag, calls `btmrvl_prepare_command`, and wakes the main service thread so the command can be sent or firmware can be woken. Removal recursively deletes the directories and frees the allocation.

## State And Persistence
Debugfs state persists for the lifetime of the registered HCI device. The files expose live `btmrvl_private` fields rather than separate cached values. Trigger fields (`pscmd`, `hscmd`, `hscfgcmd`) are consumed and cleared by `btmrvl_prepare_command`. `debugfs_data` is stored in `btmrvl_private` only when `CONFIG_DEBUG_FS` is enabled.

## Dependencies And Integration Points
Depends on Linux debugfs, simple read helpers, `kstrtol_from_user`, Bluetooth HCI debugfs root creation, and Marvell core functions from `btmrvl_main.c`. It is compiled and called only through the debugfs hooks declared in `btmrvl_drv.h`; transport code does not call it directly.

## Risks And Edge Cases
The write handlers call `btmrvl_prepare_command` synchronously before waking the thread, which can block on command wait queues from a debugfs write context. Direct debugfs mutation of mode fields has little validation beyond integer parsing and integer narrowing. If allocation fails, `priv->debugfs_data` is briefly set before the null check, but remains null because the allocation returned null. Removal assumes `hdev` still has valid drvdata and adapter state.

## Test Signals
With `CONFIG_DEBUG_FS`, verify the expected `config` and `status` files appear under the HCI device debugfs root, integer writes trigger PS/HS/HSCFG commands, nonnumeric writes return parser errors, trigger files clear after command preparation, status files reflect firmware events, and removal after HCI unregister leaves no stale debugfs entries.
