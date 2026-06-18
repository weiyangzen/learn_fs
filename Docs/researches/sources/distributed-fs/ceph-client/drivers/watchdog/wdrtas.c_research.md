# sources/distributed-fs/ceph-client/drivers/watchdog/wdrtas.c

## Purpose
`wdrtas.c` is a legacy PowerPC RTAS watchdog driver. It exposes `/dev/watchdog` and optionally `/dev/temperature`, controlling firmware surveillance through RTAS calls rather than the modern watchdog core.

## Important APIs, types, and functions
Global state includes RTAS tokens for `set-indicator`, `event-scan`, `get-sensor-state`, and `ibm,get-system-parameter`, `wdrtas_interval`, single-open atomic state, and magic-close state. Important functions are `wdrtas_set_interval`, `wdrtas_get_interval`, `wdrtas_timer_start`, `wdrtas_timer_stop`, `wdrtas_timer_keepalive`, `wdrtas_get_temperature`, `wdrtas_write`, `wdrtas_ioctl`, `wdrtas_open`, `wdrtas_close`, `wdrtas_reboot`, `wdrtas_get_tokens`, and device registration helpers.

## Control flow
Init resolves required RTAS tokens, registers the watchdog miscdevice, optionally registers the temperature miscdevice, installs a reboot notifier, and reads the initial interval. Opening starts surveillance and performs an event-scan keepalive. Writes scan for `V` if nowayout is false and keepalive by draining RTAS event-scan results. Ioctls implement support/status/bootstatus/temp/options/keepalive/timeout. Close stops only after magic close; otherwise it pings and leaves the watchdog active.

## State and persistence
The interval is held in seconds in the driver but programmed as RTAS minutes. Firmware surveillance state lives outside the kernel and may persist until changed by RTAS. The driver does not use watchdog-core device state.

## Dependencies and integration points
It depends on RTAS firmware services, miscdevice, reboot notifiers, uaccess, and watchdog ioctl ABI. Temperature support depends on the optional RTAS sensor token.

## Risks and test signals
Risks include missing RTAS tokens, minute/second rounding surprises, event-scan failures, legacy miscdevice collisions, temperature copied as one byte despite `int` storage, and `nowayout` not preventing close path logic from leaving state ambiguous. Test signals include systems with and without optional sensor/SP tokens, open exclusivity, magic close, timeout set/get, reboot notifier shutdown, and RTAS error injection.
