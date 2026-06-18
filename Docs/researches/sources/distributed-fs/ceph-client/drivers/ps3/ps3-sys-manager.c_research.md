# sources/distributed-fs/ceph-client/drivers/ps3/ps3-sys-manager.c

Purpose: PS3 system manager VUART client. It handles power/reset/thermal notifications and coordinates final poweroff/restart with the system policy module.

Important APIs/types/functions: message header and enums for service ids, attributes, events, commands, next operations, and wake sources; `ps3_sys_manager_write()`, send helpers for attributes/next-op/shutdown-request/response, `ps3_sys_manager_handle_msg()`, event/command handlers, final poweroff/restart routines, exported WOL getters/setters, and VUART port driver callbacks.

Control flow: probe registers platform power/restart ops, subscribes to all system-manager attributes, and starts async VUART reads for the minimum message length. VUART work handles one message then rearms async read. Message handling reads a fixed header, validates version/size/payload, dispatches external events and commands, and clears payload bytes for unhandled ids. Power/reset press events set `ps3_sm_force_power_off`, use a memory barrier, and signal ctrl-alt-del. Final poweroff/restart cancels async reads, sends next-op settings, requests shutdown, then spins handling messages until the system manager sends shutdown command and the driver acknowledges it.

State/dependencies: global `user_wake_sources` with a mutex in setter, global `ps3_sm_force_power_off`, VUART device state owned by `ps3-vuart`, and registered system-manager ops. Depends on PS3 LV1 firmware, reboot infrastructure, signal delivery, and VUART exported helpers.

Risks: many protocol assumptions use `BUG_ON()` for unexpected payload sizes or read failures; module remove is not supported; final shutdown loops never return; `ps3_sm_force_power_off` uses only barriers rather than a lock; async read minimum assumes all messages are 24 or 32 bytes.

Test signals: firmware-gated registration, attribute subscription, synthetic power/reset/thermal VUART messages, malformed header handling and RX clearing, WOL state changes, final poweroff/restart protocol, async read rearm, and interaction with VUART shutdown polling mode.
