## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmd.c

Purpose: this is the Libertas firmware command engine and command helper library. It builds common firmware commands, owns the fixed command buffer pool, queues and submits commands to the bus `hw_host_to_card` hook, handles synchronous waits/asynchronous callbacks, and coordinates power-save/deep-sleep constraints.

Important functions: command helpers include `lbs_update_hw_spec()`, `lbs_host_sleep_cfg()`, `lbs_set_ps_mode()`, `lbs_cmd_802_11_sleep_params()`, `lbs_set_deep_sleep()`, `lbs_set_host_sleep()`, `lbs_set_snmp_mib()`, `lbs_get_tx_power()`, `lbs_set_monitor_mode()`, `lbs_set_channel()`, `lbs_update_channel()`, `lbs_get_rssi()`, `lbs_set_11d_domain_info()`, `lbs_get_reg()`, `lbs_set_reg()`, `lbs_set_radio()`, and MAC control helpers. Queue/core APIs are `lbs_allocate_cmd_buffer()`, `lbs_free_cmd_buffer()`, `lbs_execute_next_command()`, `__lbs_cmd_async()`, `lbs_cmd_async()`, `__lbs_cmd()`, `lbs_complete_command()`, and `lbs_ps_confirm_sleep()`.

Control flow: callers allocate a free `cmd_ctrl_node`, copy the command into its 2 KiB buffer, set command/size/result, queue it, and wake the main thread. `lbs_execute_next_command()` enforces single in-flight `cur_cmd`, power-save wake rules, and optional return to PS mode when idle. `lbs_submit_command()` stamps a sequence number, calls `hw_host_to_card(MVMS_CMD, ...)`, and arms a timeout except for deep sleep. Responses are completed by `cmdresp.c`.

State and persistence: `lbs_private` stores `cmd_array`, `cmdfreeq`, `cmdpendingq`, `cur_cmd`, `seqnum`, `dnld_sent`, timers, sleep/host-sleep flags, firmware release/capability/region/MAC address, and country code. State is volatile, with selected settings mirrored into firmware.

Dependencies and integration: depends on host command structs, cfg80211 wiphy/channel data for 11d, netdev state for monitor mode, wait queues, timers, kfifo state, and bus-specific hardware send callbacks. It exports command functions used by cfg80211, debugfs, ethtool, main, and bus code.

Risks and tests: command queue correctness depends on locks, list membership, and one in-flight command. Power-save ordering is subtle: non-PS commands may trigger EXIT_PS instead of immediate submission. Deep sleep rejects commands until wake. Test signals include command timeout/retry behavior, concurrent synchronous commands, suspend/resume signals, scan/associate longer timeout paths, register debugfs access, and firmware version/region parsing.
