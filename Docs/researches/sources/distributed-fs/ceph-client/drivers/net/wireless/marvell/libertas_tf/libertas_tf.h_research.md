<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/libertas_tf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/libertas_tf.h

## Purpose
This header is the shared contract for the Libertas thin firmware driver library. It defines the firmware command IDs, command result convention, packet descriptor layouts, command payload structures, bus callback interface, and the central `struct lbtf_private` state used by `main.c`, `cmd.c`, and USB glue code.

## Important APIs, Types, And Functions
Key constants include command numbers such as `CMD_GET_HW_SPEC`, `CMD_MAC_CONTROL`, `CMD_802_11_RADIO_CONTROL`, beacon commands, and `CMD_RET(cmd)` for firmware responses. `enum mv_ms_type` classifies host-to-card payloads as data, command, txdone, or event. `enum lbtf_mode` maps firmware operating modes to passive, station, and AP behavior.

`struct lbtf_ops` is the bus abstraction: `hw_host_to_card`, `hw_prog_firmware`, and `hw_reset_device` are supplied by interface drivers such as USB. `struct lbtf_private` is the driver object backing `ieee80211_hw`; it stores bus state, command queues, locks, timers, tx skbs, mac80211 vif pointer, radio/channel state, multicast list, supported channels/rates, and current noise.

Firmware ABI structures are packed and endian annotated: `txpd`, `rxpd`, `cmd_header`, `cmd_ctrl_node`, and `cmd_ds_*` payloads for hardware spec, MAC control, multicast, mode, BSSID, radio, channel, reset, boot2 version, and beacon control/set. The command helper macro `lbtf_cmd()` temporarily normalizes `hdr.size` to the command struct size while passing the original copyback size into `__lbtf_cmd()`.

## Control Flow
The header does not execute logic, but it shapes command flow: callers allocate `cmd_ctrl_node` instances, fill a packed command payload, enqueue via `__lbtf_cmd()` or `lbtf_cmd_async()`, then receive completion through callbacks or wait queues. Data flow is similarly defined: mac80211 packets are prefixed with `txpd`; firmware RX buffers start with `rxpd`.

## State And Persistence
All state is in memory. Persistent hardware state is firmware-owned and is driven by commands. `struct lbtf_private` is volatile per-card state and contains concurrency-sensitive fields protected by `mutex lock`, `spinlock_t driver_lock`, command timers, and list heads. No on-disk persistence exists.

## Dependencies And Integration Points
The header depends on Linux kernel locking, device, kthread, and mac80211 headers plus local debug definitions. It integrates bus-specific modules through `struct lbtf_ops`, command implementation through exported prototypes, and mac80211 through `struct ieee80211_hw`, `struct ieee80211_vif`, channels, rates, and skbs.

## Risks
The packed firmware ABI is sensitive to structure size, alignment, and endian mistakes. `struct lbtf_private` centralizes many ownership domains, so changes to command, tx, or vif fields can create locking regressions. The `lbtf_cmd()` macro mutates `hdr.size` before dispatch, which is subtle and easy to misuse with incorrectly initialized command buffers.

## Test Signals
Useful validation includes building with sparse/endian checks, loading the USB thinfirm module, verifying firmware download and `CMD_GET_HW_SPEC`, exercising station/AP interface add/remove, changing channel/radio state, transmitting data and beacons, and checking command timeout/retry behavior under injected bus failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/libertas_tf.h -->
