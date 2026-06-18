# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/cmd.c

## Purpose
Implements thinfirm command management and selected firmware commands for the mac80211-based Libertas thinfirm stack. It allocates command buffers, queues async/sync commands, submits commands through transport ops, processes command responses, and updates hardware/channel/radio state.

## Important APIs And Functions
Public helpers include `lbtf_cmd_copyback()`, `lbtf_update_hw_spec()`, `lbtf_set_channel()`, `lbtf_beacon_set()`, `lbtf_beacon_ctrl()`, `lbtf_cmd_set_mac_multicast_addr()`, `lbtf_set_mode()`, `lbtf_set_bssid()`, `lbtf_set_mac_address()`, `lbtf_set_radio_control()`, `lbtf_set_mac_control()`, `lbtf_allocate_cmd_buffer()`, `lbtf_free_cmd_buffer()`, `lbtf_execute_next_command()`, `lbtf_cmd_async()`, `__lbtf_cmd()`, `lbtf_cmd_response_rx()`, and `lbtf_process_rx_command()`.

## Control Flow And State
Command buffers live in `priv->cmd_array` and are cycled through `cmdfreeq`, `cmdpendingq`, and `cur_cmd` under `driver_lock`. `__lbtf_cmd_async()` fills command header fields, increments `seqnum`, queues the command, and schedules `priv->cmd_work` on `lbtf_wq`. `lbtf_submit_command()` calls `priv->ops->hw_host_to_card()` and starts `command_timer`. Synchronous `__lbtf_cmd()` waits on the command node waitqueue. Response processing checks sequence and `CMD_RET(curcmd)`, handles firmware `0x0004` retry responses by letting timeout logic retry, invokes optional callbacks, completes waiters, and recycles nodes.

## Dependencies And Integration
Depends on `libertas_tf.h`, thinfirm main workqueue/timers, mac80211 hardware state, firmware command ABI, and transport ops supplied by USB or other bus drivers.

## Risks And Test Signals
Risks include command node leaks on interrupted waits, response/sequence mismatch, holding locks around callbacks, timeout retry behavior, region-code clamping, and async command completion without callbacks. Test signals include `GET_HW_SPEC`, channel changes, beacon programming, MAC/radio control, multicast list updates, command timeout/retry, and valid response sequence checking.
