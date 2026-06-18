# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-tx.c

Purpose: implements Vivid radio transmitter operations for RDS block output, poll, modulator get, and modulator set.

Important APIs and functions: exported functions are `vivid_radio_tx_write`, `vivid_radio_tx_poll`, `vidioc_g_modulator`, and `vidioc_s_modulator`.

Control flow: RDS write rejects control-mode TX RDS, requires whole `v4l2_rds_data` records, serializes block I/O to one filehandle, waits for time slots based on `VIVID_RDS_NSEC_PER_BLK`, copies blocks from userspace, and, when RX/TX RDS loopback is active, stores valid non-error blocks into the shared generator data array. Modulator get reports AM/FM/SW range, stereo/RDS/block-I/O capabilities, and current subchannels. Modulator set validates supported subchannel bits and stores them.

State and persistence: state is volatile in `struct vivid_dev`: TX RDS owner, last block counter, TX subchannels, RDS generator data, and TX capability/control mode flags. Written RDS blocks persist in the generator buffer until overwritten or regenerated.

Dependencies and integration points: depends on V4L2 common/event/timing APIs, Linux sleep/signal handling, Vivid core, controls, common radio definitions, and radio loopback state maintained by `vivid-radio-common.c`.

Risks: write timing is synthetic and can block indefinitely until RDS subchannel is enabled unless nonblocking is used. Only one writer can own TX RDS block I/O. Invalid/error RDS blocks are silently ignored for loopback after counting as consumed. `vidioc_s_modulator` permits only bit mask `0x13`, so capability changes must keep that mask aligned with V4L2 subchannel definitions.

Test signals: blocking/nonblocking writes, single-writer ownership, TX subchannel toggles, RX loopback of valid blocks, control-mode rejection, modulator capability queries, and userspace RDS block size validation are useful tests.
