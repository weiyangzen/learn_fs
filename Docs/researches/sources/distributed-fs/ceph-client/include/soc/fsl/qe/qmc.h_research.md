# sources/distributed-fs/ceph-client/include/soc/fsl/qe/qmc.h

Purpose: declares the QE QMC channel consumer API for obtaining channels, configuring modes/timeslots, submitting DMA reads/writes, and controlling channel direction.

Important APIs and types: phandle helpers count and get `struct qmc_chan` by phandle index, single phandle, or child node, with devm variants and `qmc_chan_put()`. `enum qmc_mode` supports transparent and HDLC. `struct qmc_chan_info` reports mode, frame sync rates, bit rates, and TX/RX timeslot counts. `struct qmc_chan_ts_info` reports available and selected TX/RX timeslot masks. `struct qmc_chan_param` configures transparent or HDLC buffer/frame sizes and CRC32. Read flags report HDLC last/first/overflow/unaligned/abort/CRC errors. APIs submit write/read DMA buffers with completion callbacks and start/stop/reset read/write/all directions.

Control flow: client drivers acquire channels from DT, inspect capabilities, configure timeslots and mode parameters, submit DMA buffers, process async completions, and start/stop/reset directions as link state changes.

State and persistence: runtime state includes channel ownership, mode/TS configuration, queued DMA buffers, and active direction state. No persistent storage is owned.

Dependencies and integration points: depends on DT/device/types/bits and integrates QMC providers with HDLC/transparent serial or telecom drivers.

Risks and test signals: risks include missing `qmc_chan_put()`, invalid timeslot masks, callback lifetime after stop/reset, DMA buffer ownership confusion, and HDLC flag interpretation. Test phandle lookup/devm cleanup, transparent and HDLC modes, CRC32 selection, read/write completion ordering, stop/reset with in-flight buffers, and timeslot reconfiguration.
