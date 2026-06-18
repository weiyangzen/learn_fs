# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/cs_dsp.c

## Purpose
This file is the Cirrus Logic DSP firmware support library. It initializes ADSP1, ADSP2, and HALO DSP descriptors; loads `.wmfw` firmware and `.bin` coefficient files; creates coefficient controls; manages boot/run/stop/power-down/hibernate transitions; exposes DSP memory access helpers; logs bus/watchdog faults; and supports write-sequence editing.

## Important APIs, Types, And Functions
The internal `struct cs_dsp_ops` abstracts core-specific behavior: firmware format validation, memory region-to-register mapping, algorithm table setup, status logging, watchdog stopping, memory/core enablement, locking, and start/stop. Public exports include initialization (`cs_dsp_adsp1_init()`, `cs_dsp_adsp2_init()`, `cs_dsp_halo_init()`), lifecycle (`cs_dsp_adsp1_power_up()`, `cs_dsp_adsp1_power_down()`, `cs_dsp_power_up()`, `cs_dsp_run()`, `cs_dsp_stop()`, `cs_dsp_power_down()`, `cs_dsp_remove()`), controls (`cs_dsp_get_ctl()`, `cs_dsp_coeff_read_ctrl()`, `cs_dsp_coeff_write_ctrl()`, acked-control write helpers), memory (`cs_dsp_read_raw_data_block()`, `cs_dsp_read_data_word()`, `cs_dsp_write_data_word()`, `cs_dsp_remove_padding()`), diagnostics, chunk formatting, and write-sequence helpers.

Firmware parsing is split between `cs_dsp_load()` for WMFW regions and `cs_dsp_load_coeff()` for WMDR/bin coefficient blocks. Algorithm discovery reads DSP memory headers in `cs_dsp_adsp1_setup_algs()`, `cs_dsp_adsp2_setup_algs()`, or `cs_dsp_halo_setup_algs()` and creates `struct cs_dsp_alg_region` entries that coefficient controls use for base fixups.

## Control Flow, State, And Persistence
`cs_dsp_common_init()` initializes list heads, `pwr_lock`, names, client ops, and debugfs defaults. Power-up loads firmware, sets up algorithms, loads coefficients, initializes readable control caches, syncs dirty controls, and marks `booted`. `cs_dsp_run()` enables core, calls client pre-run, syncs controls, optionally locks memory/MPU, starts core, marks `running`, and calls post-run. `cs_dsp_stop()` signals firmware shutdown through host-event controls, stops watchdog, logs status, calls stop callbacks, clears `running`, and disables/stops core while preserving loaded memory. `cs_dsp_power_down()` disables memory, clears firmware IDs, disables controls, and frees algorithm regions.

Runtime state is kept in the caller-owned `struct cs_dsp`: `booted`, `running`, `hibernating`, firmware IDs/names, control list, algorithm-region list, memory map, regmap, and callbacks. Coefficient controls persist cached values and dirty state across stop/hibernate boundaries, with volatile controls requiring live hardware access.

## Dependencies And Integration Points
The library depends on regmap, firmware blobs described by `linux/firmware/cirrus/wmfw.h`, public `linux/firmware/cirrus/cs_dsp.h`, debugfs, KUnit static stubs, vmalloc, and client-provided `cs_dsp_client_ops`. Exports use namespace `FW_CS_DSP` for most APIs. Debugfs exposes boot/run/hibernate state, firmware IDs, loaded filenames, and parsed controls.

## Risks And Test Signals
Risk is high because file-format parsing writes directly to device memory. Important defenses include magic/version/core checks, overflow checks on region/block lengths, DMA-safe scratch buffers, and lock assertions on control paths. Remaining risks include off-by-one address conversion across packed/unpacked memories, stale dirty caches, callback error rollback, unsupported control flags, and write-sequence terminator corruption. Test signals are the extensive KUnit suite using mock WMFW/bin builders and mock regmaps, plus hardware tests for lifecycle, hibernate resync, bus/watchdog diagnostics, debugfs, long-offset coefficient blocks, and malformed firmware rejection.
