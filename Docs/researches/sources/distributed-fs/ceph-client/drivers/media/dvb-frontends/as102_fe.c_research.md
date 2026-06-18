# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe.c

## Purpose
`as102_fe.c` implements a DVB-T frontend shim for Abilis AS102 receivers. It translates Linux DVB frontend operations to device-specific callback operations supplied by the parent AS102 transport driver.

## Important APIs, Types, And Functions
`struct as102_state` contains the DVB frontend, cached demod stats, callback table, private parent pointer, eLNA config, signal strength, and BER. `as102_attach()` allocates state, installs `as102_fe_ops`, stores callbacks, and returns a frontend. Important operations are `as102_fe_set_frontend()`, `as102_fe_get_frontend()`, `as102_fe_read_status()`, DVBv3 metric readers, `as102_fe_ts_bus_ctrl()`, and `as102_fe_release()`.

## Control Flow
Set-frontend converts DVB property cache values into packed AS10x tuning arguments: frequency in kHz, bandwidth, guard interval, modulation, transmission mode, hierarchy, and code rate selection. It then calls parent `set_tune`. Get-frontend calls `get_tps` and maps hardware TPS fields back into DVB properties. Read-status calls `get_status`, updates cached signal/BER, maps tune state into FE status flags, clears demod stats if not locked, and calls `get_stats` when locked. TS bus control calls parent `stream_ctrl` with acquire flag and eLNA config.

## State And Persistence
The driver caches demod stats, signal strength, and BER inside `as102_state`. There is no persistent storage. Cached stats are cleared on unlock and freed on release.

## Dependencies And Integration Points
The file depends on DVB frontend core and AS10x command structure definitions from `as102_fe_types.h`. It does not know the USB/control transport; all hardware access is through `struct as102_fe_ops` callbacks.

## Risks
Callback pointers are assumed valid. Unsupported or AUTO values often map to device `UNKNOWN` constants rather than hard errors, so bad tuning input may fail only by not locking. `as102_fe_read_signal_strength()` uses a questionable arithmetic scaling expression that can overflow or produce nonstandard values depending on `signal_strength`. Only PAL/NTSC concerns are irrelevant here; this is DVB-T only.

## Test Signals
Mock callback tests can verify DVB-to-AS10x mapping. Hardware tests should tune 6/7/8 MHz channels, test hierarchy/code-rate selection, lock/unlock status transitions, stats refresh, and TS bus acquire/release behavior.
