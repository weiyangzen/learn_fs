# sources/distributed-fs/ceph-client/sound/core/init.c

## Purpose
`init.c` is the ALSA card lifecycle core. It allocates cards, assigns card slots and ids, initializes control and proc infrastructure, registers card devices, tracks open files for hot-unplug, disconnects active file operations, frees resources, exposes card sysfs attributes, and provides PM power wait helpers.

## Important APIs, Types, and Functions
Public APIs include `snd_device_alloc()`, `snd_card_new()`, `snd_devm_card_new()`, `snd_card_free_on_error()`, `snd_card_ref()`, `snd_card_locked()`, `snd_card_disconnect()`, `snd_card_disconnect_sync()`, `snd_card_free_when_closed()`, `snd_card_free()`, `snd_card_set_id()`, `snd_card_add_dev_attr()`, `snd_card_register()`, `snd_component_add()`, `snd_card_file_add()`, `snd_card_file_remove()`, `snd_power_ref_and_wait()`, and `snd_power_wait()`. `snd_monitor_file` tracks open files and their original file ops during shutdown.

## Control Flow and State
Global state includes `snd_cards[]`, `snd_cards_lock` bitmap, `snd_card_mutex`, `shutdown_files`, and `shutdown_lock`. Card creation chooses a slot using module `slots[]` preferences, empty-slot fallback, and `snd_ecards_limit`, then initializes device lists, control lists, file lists, wait queues, card device, control minors, proc card root, and debugfs/value buffers when configured. Registration adds the card device, handles managed devres actions, registers all component devices, derives or uniquifies the card id, publishes `snd_cards[number]`, registers proc info, and notifies OSS mixer emulation.

Disconnect marks shutdown under `files_lock`, replaces every active file's `f_op` with `snd_shutdown_f_ops`, wakes PM sleepers, notifies OSS and devices, synchronizes optional IRQ, removes proc/debugfs/card device publication, clears the global card slot, and syncs power refs. File removal restores original fops refs and wakes `remove_sleep` when the file list empties. Free waits on a completion triggered by device release and then frees devices, private data, card info, debug buffers, and the card allocation.

## Dependencies and Integration Points
This file integrates almost every ALSA core subsystem: control creation, proc info, generic devices, OSS mixer notifications, debugfs, sysfs, devres, PM, and card file tracking used by hwdep/PCM/rawmidi/etc.

## Risks and Test Signals
Risks are hot-unplug races, double-free in managed versus unmanaged cards, card id conflicts, file op replacement lifetime, and slot allocation bugs with module parameters. Tests should cover manual and devm card creation, registration failure paths, card id sysfs writes, duplicate ids, open-file disconnect and release, synchronous disconnect waiting, PM wait during shutdown, OSS mixer callbacks, and repeated register/unregister cycles.
