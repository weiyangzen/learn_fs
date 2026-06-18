# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2-fe.c

Purpose: implements the DVB frontend operations for the TerraTec/qanu Cinergy T2 USB2 DVB-T receiver. Unlike AF9005, the demodulation details are largely hidden behind the device firmware protocol, so this file converts DVB frontend parameters to device messages and translates device status messages into DVB frontend status/statistics.

Important APIs, types, and functions: `compute_tps()` maps Linux DVB-T parameters to a 16-bit TPS field following ETSI DVB-T bit placement. `struct cinergyt2_fe_state` embeds `struct dvb_frontend`, stores the parent `dvb_usb_device`, owns a 64-byte control buffer and mutex, and caches `struct dvbt_get_status_msg`. `cinergyt2_fe_attach()` allocates state and installs `cinergyt2_fe_ops`. Frontend callbacks implement status, BER, uncorrected blocks, strength, SNR, tune settings, tuning, sleep/init, and release.

Control flow: `set_frontend()` locks the frontend data mutex, overlays the control buffer with `struct dvbt_set_parameters_msg`, fills command, frequency in kHz, bandwidth code 6/7/8, computed TPS, and flags, then sends the message through `dvb_usb_generic_rw()` and expects a two-byte reply. `read_status()` sends `CINERGYT2_EP1_GET_TUNER_STATUS`, copies the packed response into cached status, and derives `FE_HAS_*` flags from gain and lock bits. BER/SNR/strength/uncorrected-block reads return fields from the most recent cached status. Tune settings request an 800 ms minimum delay.

State and persistence: frontend state is per attach and freed on release. The cached status persists until the next successful status read; statistic callbacks do not refresh hardware themselves. Hardware tuning state persists in device firmware after set-parameters command. The mutex protects only this frontend buffer, distinct from the core driver's shared control buffer.

Dependencies and integration points: depends on command and message definitions in `cinergyT2.h`, DVB USB generic bulk control, endian conversion helpers, and DVB frontend ops. It is attached by `cinergyt2_frontend_attach()` in `cinergyT2-core.c`.

Risks: BER/SNR/strength can return stale or zeroed data if userspace reads them before `read_status()` succeeds. `compute_tps()` silently maps unknown/AUTO values to default TPS bits, which is intentional but may hide unsupported combinations. Status lock logic clears `FE_HAS_LOCK` unless carrier, Viterbi, and sync are also set, so device firmware lock bits are filtered. The code logs an error via `err()` inside a variable named `err`, relying on macro/function namespace behavior that is potentially confusing.

Test signals: tune DVB-T channels with 6/7/8 MHz bandwidth, verify TPS encoding for modulation/FEC/guard/hierarchy/transmission modes, confirm lock-bit mapping under weak/no signal, read stats before and after status refresh, validate 800 ms tune delay behavior, and run repeated attach/release cycles.
