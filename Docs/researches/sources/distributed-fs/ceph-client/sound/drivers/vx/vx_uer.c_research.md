# sources/distributed-fs/ceph-client/sound/drivers/vx/vx_uer.c

Purpose: handles VX IEC958/UER status bits and sample clock management. It selects internal or external clock sources, programs board clock registers, reads external digital input status, and updates detected frequency.

Important APIs, types, and functions: internal helpers include `vx_modify_board_clock()`, `vx_modify_board_inputs()`, `vx_read_one_cbit()`, `vx_write_one_cbit()`, `vx_read_uer_status()`, `vx_calc_clock_from_freq()`, and `vx_change_clock_source()`. Exported/common functions are `vx_set_internal_clock()`, `vx_set_iec958_status()`, `vx_set_clock()`, and `vx_change_frequency()`.

Control flow: reset and mixer paths call `vx_set_internal_clock()` and `vx_set_iec958_status()`. `vx_set_clock()` first syncs the desired audio source if possible, then selects UER sync for external mode or auto-digital mode, otherwise selects internal quartz and programs clock divisors when the rate changes. It updates `chip->freq` and sends `CMD_MODIFY_CLOCK` with FIFO resync. Frequency-change IRQ events call `vx_change_frequency()`, which ignores internal clock mode, reads UER status, classifies consumer/professional/not-present by C-bit 0, and updates `freq_detected` for 32/44.1/48 kHz.

State and persistence: state is live in `vx_core`: `clock_source`, `clock_mode`, `freq`, `freq_detected`, `uer_detected`, `uer_bits`, audio source fields, and stale status. No persistent state exists. `chip->lock` protects register access; mixer callers use `mixer_mutex` around user-visible clock/IEC958 fields.

Dependencies and integration: uses VX register ops (`vx_inb/outb`, `vx_inl/outl`), board `set_clock_source` op, DSP RMH commands, mixer audio-source sync, and PCM prepare clock negotiation.

Risks: `vx_calc_clock_from_freq()` has BUG checks and clamps unsupported low frequencies to a fixed minimum code; unusual rates can be accepted by PCM constraints but mapped imprecisely. IEC958 status writes loop bit-by-bit with separate locks, so readers could see transient partial updates at hardware level. External clock changes include fixed delays and assume board status masks are reliable. Test signals include internal divisor calculation across supported rates, source switching with DAC mute/unmute, auto mode with analog versus digital source, UER mode/frequency detection, stale-chip no-op behavior, and IEC958 bit round-trips through mixer controls.
