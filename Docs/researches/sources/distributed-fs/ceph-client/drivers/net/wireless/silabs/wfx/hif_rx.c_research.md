# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_rx.c

Purpose: Dispatches WFx HIF confirmations and indications received from firmware.

Important APIs and functions: `wfx_handle_rx()` is the public dispatcher. Confirmation handlers include generic command confirmation, single TX confirm, and multi-TX confirm. Indication handlers process startup, wakeup, RX, event, PM complete, scan complete, join complete, suspend/resume TX, generic stats, asynchronous errors, and exceptions.

Control flow and integration: BH passes each complete SKB to `wfx_handle_rx()`. RX data indications are handed to `wfx_hif_receive_indication()` and then `wfx_rx_cb()`. If a synchronous command lock is held and the ID matches `hif_cmd.buf_send`, generic confirmation copies the reply/status and completes `hif_cmd.done`. Otherwise the dispatcher searches the static handler table. Error and exception indications log payloads and freeze the chip.

State and persistence: Updates `wdev->hw_caps`, completes `firmware_ready`, completes per-vif `set_pm_mode_complete` and `scan_complete`, updates RX stats and TX power loop info under locks, schedules/cancels beacon loss work, and sets `chip_frozen` on firmware fatal errors.

Dependencies: Depends on scan, BH, station, data RX/TX callbacks, HIF command/general layouts, SKB lifetime rules, and mac80211 notifications.

Risks and test signals: Risks include unexpected confirmation while no command is pending, command/reply ID mismatch, reply buffer length mismatch, indications for missing vifs, error/exception recovery freezing TX, and SKB lifetime differences for RX data vs other messages. Tests should cover all handler IDs, multi-TX confirm, startup completion, PM/scan completions, BSS lost/regained, generic stats updates, firmware error/exception, unknown indications, and mismatched command confirmations.

Test signals: Source read size: 391 lines, 11976 bytes.
