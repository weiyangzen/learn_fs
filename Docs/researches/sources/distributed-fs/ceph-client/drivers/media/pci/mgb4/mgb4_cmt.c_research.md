# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_cmt.c

- Purpose: Programs FPGA Clock Management Tile register tables for supported input frequency ranges and output pixel clocks.
- Important APIs/types/functions: Large precomputed `cmt_vals_out`, `cmt_vals_in`, address tables, `cmt_freq`, `freq_srch()`, `mgb4_cmt_set_vout_freq()`, and `mgb4_cmt_set_vin_freq_range()`.
- Control flow: Output configuration chooses nearest supported frequency, gates output config, asserts CMT programming bit, writes the selected table to CMT registers, deasserts programming bit, and restores config. Input range programming selects one of two tables with `array_index_nospec` and writes input CMT registers similarly.
- State and persistence: CMT register state persists in FPGA until reprogrammed/reset; `voutdev->freq` and `vindev->freq_range` track chosen values in RAM.
- Dependencies and integration points: Called by vout FPGA init and output `pclk_frequency` sysfs store, and by input `frequency_range` sysfs store.
- Risks: Nearest-frequency selection can surprise users requesting unsupported clocks. Tables are magic hardware data; any bad entry can break video timing. Reprogramming while queues run is guarded by callers, not the CMT functions themselves.
- Test signals: Test sysfs pclk/frequency_range writes, nearest-frequency reporting, video lock over supported clock range, and concurrent queue-start rejection.
