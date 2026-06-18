# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/main.c

## Purpose

`main.c` is the DVM op-mode module and lifecycle core. It registers the `iwldvm` op-mode and rate control, starts/stops device instances, selects device-family configuration, reads and parses NVM, initializes driver state and contexts, manages firmware alive/down/restart flows, schedules deferred work/timers, handles firmware errors and event logs, configures NIC registers, and implements transport-facing op-mode callbacks.

## Important APIs, Types, and Functions

Key exported or callback functions include `iwl_update_chain_flags()`, `iwlagn_send_beacon_cmd()`, `iwl_send_statistics_request()`, `iwl_alive_start()`, `iwl_down()`, `iwlagn_prepare_restart()`, `iwl_cancel_deferred_work()`, `iwl_dump_nic_event_log()`, `iwlagn_lift_passive_no_rx()`, `iwl_op_mode_dvm_start()`, `iwl_op_mode_dvm_stop()`, transport callbacks in `iwl_dvm_ops`, and module `iwl_init()`/`iwl_exit()`.

Important local helpers handle beacon TIM parsing/update, BT runtime/full-concurrency work, periodic statistics, continuous event tracing, TX flush work, RXON context initialization, CT-kill config, runtime calibration config, TX antenna config, legacy BT config, station clearing, runtime calibration work, driver init/uninit, hardware/NVM parameter checks, firmware error dumps, software reset, NIC config, queue stop/wake, SKB free, and RF-kill state propagation.

## Control Flow

Module init registers rate control then the `iwldvm` op-mode. `iwl_op_mode_dvm_start()` allocates mac80211 hardware/private op-mode state, selects `priv->lib`, configures transport command groups/queues/no-reclaim commands/RX buffer size, enters op-mode, starts hardware long enough to read EEPROM/OTP, stops hardware, parses NVM, checks versions and SKU, derives MAC addresses and chain counts, initializes queues/driver state/work/timers/RX handlers/power/thermal/context metadata, registers with mac80211, and registers debugfs. Cleanup unwinds in reverse.

Runtime bring-up occurs after mac80211 start via `iwl_alive_start()`: mark alive, optionally start ucode tracing, configure BT coexistence and priority tables, request runtime calibration, wake queues, send TX antenna config, initialize or preserve RXON association state, reset runtime calibration, mark ready, commit RXON, configure CT-kill, and update power mode. Down/restart paths cancel scan, set exit-pending, clear firmware and driver station/key state, reset BT state, stop queues, stop transport, preserve selected status bits, clear beacon SKB, and prepare mac80211 restart.

Firmware error handling records FW error status, aborts notification waits, dumps error/event logs unless command-queue-full CT-kill applies, rate-limits continuous reloads, and queues restart work if enabled.

## State and Persistence Behavior

This file owns op-mode registration, `priv->status` transitions (`ALIVE`, `READY`, `EXIT_PENDING`, `FW_ERROR`, RF-kill), `ucode_loaded`, current ucode type, event-log cursor counters, firmware reload counters, workqueue/timers, queue stop counts and `transport_queue_stop`, RXON context command IDs/modes/queues, beacon command/SKB state, NVM-derived addresses, BT defaults, calibration command IDs, power/thermal init state, station/key clearing, debugfs registration, and transport configuration fields.

Hardware/firmware state touched includes NIC start/stop, EEPROM reads, CSR/PRPH NIC config, BT/CT-kill/calibration/TX antenna/statistics/beacon commands, SRAM event/error log reads, and mac80211 queue stop/wake.

## Dependencies and Integration Points

`main.c` integrates transport op-mode APIs, firmware image/capability data, NVM parsing from `eeprom.c`, device-family configs from `devices.c`, mac80211 registration from `mac80211.c`, scan/RX/TX/station/rate/calibration/thermal/debugfs helpers, Linux module infrastructure, and trace/debug logging.

## Risks and Edge Cases

Probe has many partial-initialization labels; incorrect unwind ordering can leak workqueues, NVM blobs, or registered mac80211 state. Restart intentionally preserves some BT state while clearing most device state. Status-bit masking in `iwl_down()` is compact and easy to misread. Continuous event tracing handles firmware write-pointer/wrap races; any simplification may drop or over-read logs. Queue stop/wake uses refcounts per mac80211 queue and must remain balanced. Firmware reload rate limiting stops repeated restarts after too many fast failures.

## Test Signals

Test module load/unload, op-mode start failure injection at each probe stage, NVM version/SKU rejection, mac80211 registration failure unwind, normal start/stop, firmware alive sequence, CT-kill config variants, firmware error/restart rate limiting, event/error log dumping with bogus pointers and wrap cases, queue full/not-full balancing, passive no-rx lifting, RF-kill state propagation, and transport op-mode enter/leave ordering.
