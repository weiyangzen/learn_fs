# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_main.c

## Purpose
Implements the Marvell Bluetooth common HCI driver core, used by the SDIO transport. It manages interrupt wakeups, Marvell vendor event handling, synchronous vendor command submission, power-save and host-sleep control, device-tree calibration/configuration, TX queue servicing from a kernel thread, HCI device registration, and card add/remove lifecycle.

## Important APIs, Types, And Functions
- Exported lifecycle functions are `btmrvl_add_card`, `btmrvl_register_hdev`, and `btmrvl_remove_card`.
- Exported event and interrupt functions are `btmrvl_interrupt`, `btmrvl_check_evtpkt`, and `btmrvl_process_event`.
- Exported command helpers include `btmrvl_send_module_cfg_cmd`, `btmrvl_pscan_window_reporting`, `btmrvl_send_hscfg_cmd`, `btmrvl_enable_ps`, `btmrvl_enable_hs`, and `btmrvl_prepare_command`.
- HCI callbacks include `btmrvl_send_frame`, `btmrvl_flush`, `btmrvl_close`, `btmrvl_open`, `btmrvl_setup`, `btmrvl_set_bdaddr`, and `btmrvl_wakeup`.
- The main worker is `btmrvl_service_main_thread`, which serializes interrupt processing, firmware wakeup, and packet download to the bus transport.

## Control Flow
`btmrvl_add_card` allocates private and adapter state, initializes queues and wait queues, starts the service kthread, records the transport card, and marks TX download ready. The transport later calls `btmrvl_register_hdev`, which allocates/registers an HCI device and installs common callbacks. HCI setup sends module bring-up, reads device-tree wake/calibration data, routes SCO to host, enables scan-window reporting if supported, enables power save, and sends host-sleep configuration.

Outgoing HCI packets are queued by `btmrvl_send_frame` unless the adapter is suspending or suspended. The service thread sleeps until an interrupt, pending TX, or wakeup retry exists. It processes hardware interrupt status through the transport callback, wakes sleeping firmware if needed, skips TX while power-save sleep or suspend is active, and otherwise sends one queued packet with a Marvell four-byte length/type header through `hw_host_to_card`. Synchronous vendor commands are queued as `MRVL_VENDOR_PKT`, set `sendcmdflag`, wake the service thread, and wait for command completion. Incoming command-complete events wake the command wait queue and suppress vendor command responses from the normal HCI path; Marvell vendor events update PS/HS/module state and may consume the skb.

## State And Persistence
State lives in `btmrvl_private`, `btmrvl_device`, and `btmrvl_adapter`. Persistent fields include TX skb queue, power-save mode and state, host-sleep mode/state, wakeup retry count, interrupt count, command completion flag, send-command flag, GPIO/gap setting, suspend flags, hardware register buffer, service thread, wait queues, and surprise-removal flag. Device-tree calibration is downloaded during setup and not retained separately. Removal wakes command and host-sleep waiters, stops the thread, unregisters/frees HCI, frees adapter buffers, and releases private state.

## Dependencies And Integration Points
Depends on Bluetooth HCI core, Marvell SDIO transport definitions from `btmrvl_sdio.h`, SDIO device access through the transport callbacks, device-tree properties `marvell,wakeup-pin`, `marvell,wakeup-gap-ms`, and `marvell,cal-data`, kernel kthreads/wait queues/skb queues, and optional debugfs initialization/removal. It integrates with board bindings for wake/calibration data and with the HCI stack through standard open/close/flush/send/setup/set_bdaddr/wakeup callbacks.

## Risks And Edge Cases
`btmrvl_enable_ps` and `btmrvl_download_cal_data` log command failures but return zero, so setup may continue after failed PS or calibration commands. `btmrvl_send_sync_cmd` waits for command completion without directly inspecting command status beyond event side effects. The service thread processes at most one TX skb per wake cycle, so sustained throughput depends on repeated wake conditions. Power-save sleep can delay TX until firmware wake succeeds, and wakeup retry handling must avoid livelock. Surprise removal must wake all waiters to avoid blocked command or host-sleep waits. Device-tree calibration requires an exact 28-byte property.

## Test Signals
Useful coverage includes module bring-up/shutdown responses, vendor command timeout and surprise-removal wakeups, command-complete filtering for vendor OGF, PS enable/disable events, host-sleep enable success/failure/timeout, firmware wake before TX while asleep, suspend/suspending rejection in `send_frame`, malformed or unknown Marvell vendor events, BDADDR set command failure, device-tree wake and calibration properties, service-thread shutdown, and debugfs-triggered command paths.
