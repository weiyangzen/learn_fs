# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/main.c

## Purpose
Provides the shared full-firmware Libertas driver core: netdev lifecycle, main service thread, command/event/TX scheduling, multicast programming, firmware setup, suspend/resume helpers, adapter allocation/free, debugfs/cfg80211 registration, and exported bus-driver entry points.

## Important APIs And Functions
Public/exported functions include `lbs_fw_index_to_data_rate()`, `lbs_set_iface_type()`, `lbs_start_iface()`, `lbs_stop_iface()`, `lbs_host_to_card_done()`, `lbs_set_mac_address()`, `lbs_suspend()`, `lbs_resume()`, `lbs_add_card()`, `lbs_remove_card()`, `lbs_start_card()`, `lbs_stop_card()`, `lbs_queue_event()`, and `lbs_notify_command_response()`. Netdev operations are open, stop, xmit, MAC address, and multicast update. `lbs_thread()` is the central scheduler.

## Control Flow And State
Transports call into this core through `hw_host_to_card` and response/event callbacks. `lbs_thread()` sleeps until work appears, then processes command responses, firmware events, command timeouts, sleep confirmation, queued commands, and pending TX in that order. State is held in `lbs_private`: `fw_ready`, `dnld_sent`, `cur_cmd`, command queues, response buffers, event FIFO, power-save/deep-sleep flags, `tx_pending_len`, timers, netdev pointers, and mesh pointers. `driver_lock`, waitqueues, timers, and workqueues coordinate access.

## Dependencies And Integration
Depends on cfg80211 setup, debugfs, command helpers, mesh support, Linux netdev APIs, kthreads, kfifo, and bus-specific drivers. Bus drivers call `lbs_add_card()` then assign transport callbacks before calling `lbs_start_card()`.

## Risks And Test Signals
Risks include serialization bugs around `dnld_sent`, response buffer flipping, command timeout recovery, TX lockup reset, teardown while work or commands are pending, and multicast updates across station and mesh devices. Test signals include card add/start/stop/remove, netdev open/close, command timeout reset, TX queue wake, multicast mode programming, suspend/resume, and mesh-disabled module parameter behavior.
