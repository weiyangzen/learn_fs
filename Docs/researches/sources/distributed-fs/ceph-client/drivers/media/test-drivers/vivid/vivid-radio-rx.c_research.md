# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-rx.c

Purpose: implements Vivid radio receiver userspace operations: RDS block reading, poll, frequency band enumeration, hardware seek simulation, tuner status reporting, and audio mode setting.

Important APIs and functions: exported functions are `vivid_radio_rx_read`, `vivid_radio_rx_poll`, `vivid_radio_rx_enum_freq_bands`, `vivid_radio_rx_s_hw_freq_seek`, `vivid_radio_rx_g_tuner`, and `vivid_radio_rx_s_tuner`.

Control flow: RDS read rejects control-mode RDS, serializes ownership of block I/O to one filehandle, initializes/regenerates RDS blocks based on elapsed `VIVID_RDS_NSEC_PER_BLK`, blocks or returns `-EWOULDBLOCK` until data is available, injects block errors based on signal quality, and copies whole `v4l2_rds_data` records to userspace. Hardware seek validates mode/range/wrap constraints and computes the next channel spacing but does not store the new frequency in this snapshot. `g_tuner` reports capability flags, signal strength, AFC, mono/stereo/RDS subchannels, and optionally refreshes RDS controls.

State and persistence: state is volatile in `struct vivid_dev`: RDS owner filehandle, last block counters, RDS alternate state, generated RDS data, RX frequency, signal quality, RDS enable/control mode flags, hardware seek mode/prog-limits, and RX audio mode.

Dependencies and integration points: depends on V4L2 common/event/timing APIs, Linux sleep/signal handling, Vivid core, common radio helpers, RDS generator, and V4L2 filehandle ownership.

Risks: hardware seek currently computes `freq` but returns without assigning `dev->radio_rx_freq`, so it may validate seek behavior without moving the tuner. RDS read uses time-based block generation and sleeps in 20 ms increments, which can be timing-sensitive. Only one RDS block-I/O reader is allowed. Signal-quality error injection is random and can make tests nondeterministic unless tuned to strong signal.

Test signals: RDS blocking/nonblocking reads, one-reader ownership, weak-signal error injection, RDS enable/disable, tuner capability flags for seek modes and RDS mode, hardware seek with bounded/wrap/prog-limits, and RX/TX RDS loopback validate this module.
