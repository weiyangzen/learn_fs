# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-stream.c

Purpose: manages DICE duplex stream resources, rate mode selection, clock selection, ISO channel programming, global enable, bus reset update, and stream locking.

Important APIs/functions: `snd_dice_stream_get_rate_mode`, `snd_dice_stream_reserve_duplex`, `snd_dice_stream_start_duplex`, `snd_dice_stream_stop_duplex`, `snd_dice_stream_init_duplex`, `snd_dice_stream_destroy_duplex`, `snd_dice_stream_update_duplex`, `snd_dice_stream_detect_current_formats`, and lock helpers. Key internals include `select_clock`, `get_register_params`, `keep_resources`, `keep_dual_resources`, `start_streams`, and `finish_session`.

Control flow and state: reserve stops existing sessions when needed, selects clock, reads stream register layout, configures AM824 parameters and ISO resources for each TX/RX stream, and records period/buffer events. Start updates resources after bus generation changes, programs TX/RX ISO channel registers and TX speed, sets global enable, starts the AMDTP domain with sequence replay, and waits briefly for readiness. Stop clears stream registers/global enable, stops the domain, and frees resources when no clients remain.

Dependencies/integration: uses DICE transactions/registers, FireWire ISO resources, AMDTP/AM824, clock notification completion, PCM/MIDI counters, and detector caches. Risks include high-rate dual-wire channel doubling, cache mismatch with hardware registers, short notification/readiness timeouts, bus reset reinitialization, and all-stream-or-none assumptions. Test signals include reserve/start/stop across rate changes, no cache mismatch logs, successful bus reset recovery, and correct high-rate channel mapping.
