# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_common.h

## Purpose
This header provides shared utility wrappers and cross-module declarations for the RSI common core, especially event/thread helpers used by TX, SDIO RX, USB RX, and coexistence worker threads.

## Important APIs, Types, and Functions
It defines `EVENT_WAIT_FOREVER`, `FIRMWARE_RSI9113`, `QUEUE_NOT_FULL`, `QUEUE_FULL`, inline helpers `rsi_init_event`, `rsi_wait_event`, `rsi_set_event`, `rsi_reset_event`, `rsi_create_kthread`, and `rsi_kill_thread`, plus prototypes for common/mac80211 lifecycle and packet APIs such as `rsi_mac80211_detach`, `rsi_mac80211_rfkill_exit`, `rsi_get_connected_channel`, `rsi_91x_init`, `rsi_91x_deinit`, `rsi_read_pkt`, `rsi_config_wowlan`, `rsi_find_sta`, `rsi_get_vif`, and `rsi_roc_timeout`.

## Control Flow
Event helpers implement an inverted condition convention: initialized/reset events have condition `1`, set events change it to `0` and wake waiters, and waiters block until it becomes `0`. Thread creation wraps `kthread_run`; thread killing sets `thread_done`, wakes the event, and waits for the thread's completion.

## State and Persistence Behavior
The inline helpers mutate `struct rsi_event` atomics/wait queues and `struct rsi_thread` task/completion state. No persistent storage is involved.

## Dependencies and Integration Points
It depends on `linux/kthread.h` and types from `rsi_main.h`/mac80211 declarations in compilation units. It is included by core, SDIO, USB, management, power-save, and coexistence code.

## Risks
The event convention is easy to misuse because "set" means condition zero. `rsi_kill_thread` assumes the thread was successfully created and will always complete. `rsi_create_kthread` casts `PTR_ERR` to `int`, which is normal but loses type annotation. Prototypes must match implementations gated by `CONFIG_PM` and optional modules.

## Test Signals
Thread start/stop for TX/RX/coex workers, wake-before-wait cases, repeated event resets, module unload under idle and active traffic, and builds with PM/coex/debugfs combinations validate this header.
