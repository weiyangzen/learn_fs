<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/main.c

## Purpose
`main.c` is the core Libertas thin firmware mac80211 driver library. It owns module lifetime, shared workqueue creation, adapter initialization, mac80211 operation callbacks, firmware programming handoff, tx/rx conversion between firmware descriptors and mac80211 skbs, command timeout retry work, and exported card add/remove APIs used by interface drivers.

## Important APIs, Types, And Functions
The exported surface is `lbtf_add_card()`, `lbtf_remove_card()`, `lbtf_rx()`, `lbtf_send_tx_feedback()`, and `lbtf_bcn_sent()`. Internal mac80211 callbacks include `lbtf_op_tx`, `lbtf_op_start`, `lbtf_op_stop`, `lbtf_op_add_interface`, `lbtf_op_remove_interface`, `lbtf_op_config`, multicast/filter handlers, `lbtf_op_bss_info_changed`, and `lbtf_op_get_survey`.

`lbtf_cmd_work()` processes command responses and timeout-driven retries, while `command_timer_fn()` marks the active command timed out and queues command work. `lbtf_tx_work()` selects either buffered broadcast/multicast AP power-save frames or a normal queued skb, prepends `txpd`, programs per-packet rate, and calls `ops->hw_host_to_card()`.

## Control Flow
Module init allocates `lbtf_wq`; module exit destroys it. A bus driver calls `lbtf_add_card()`, which allocates `ieee80211_hw`, initializes command queues/timer/locks, sets 2.4 GHz channel and rate tables, registers supported bands, initializes work items, calls `hw_prog_firmware()`, reads hardware spec, validates firmware version, turns the radio off, and registers with mac80211.

Mac80211 tx stores one skb in `priv->skb_to_tx`, queues tx work, and stops queues until firmware tx feedback arrives. Firmware tx feedback clears status, reports ACK when appropriate, strips `txpd`, calls `ieee80211_tx_status_irqsafe()`, and wakes or continues queues. RX starts with `rxpd`, builds `ieee80211_rx_status`, adjusts for Marvell rate numbering, conditionally adds padding for QoS/A4/A-MSDU headers, and calls `ieee80211_rx_irqsafe()`.

Interface add switches firmware mode to AP/mesh or STA and sets the MAC address. BSS info changes push beacons, BSSID, and preamble changes to firmware. Stop drains pending commands, cancels work, flushes buffered broadcast frames, and turns radio off.

## State And Persistence
The module stores global debug state and workqueue pointer. Per-card state is in `lbtf_private`: current vif, `skb_to_tx`, in-flight `tx_skb`, command queues, firmware version, channel/frequency, radio state, multicast list, beacon PS buffer, and noise. State is volatile and re-derived on probe; firmware settings persist only while device firmware remains running.

## Dependencies And Integration Points
The file integrates with mac80211 (`ieee80211_ops`, queues, beacon helpers, survey reporting), Linux workqueues/timers/skbs, and bus-specific callbacks. It calls command-layer helpers declared in `libertas_tf.h`, including radio, MAC, multicast, mode, BSSID, beacon, channel, and hardware-spec commands.

## Risks
`lbtf_tx_work()` assumes `priv->vif` is valid when work runs; lifecycle ordering around interface removal and queued tx work is important. Single pending `skb_to_tx`/`tx_skb` state constrains concurrency and can fail badly if queue stop/wake sequencing regresses. Command timeout retry logic resubmits at the head of the pending queue and must preserve list ownership under `driver_lock`. RX padding manipulation uses `memmove`/`skb_reserve` and is sensitive to skb headroom.

## Test Signals
Signals include successful module load/unload, firmware version acceptance, mac80211 hardware registration, station association, AP/mesh beacon update, multicast filter programming, channel changes, tx feedback queue wakeups, RX signal/noise reporting, survey noise reads, and command timeout retries under mocked or unplugged hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/main.c -->
