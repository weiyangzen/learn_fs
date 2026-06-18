# sources/distributed-fs/ceph-client/drivers/soundwire/intel.c

## Purpose

`intel.c` is the Intel SoundWire master hardware-ops implementation for older Cadence/Intel SHIM generations, exported as `sdw_intel_cnl_hw_ops`. It covers SHIM power sequencing, wake control, synchronized bank switching, PDI discovery/configuration, ALH stream register programming, debugfs register dumps, and ASoC CPU DAI registration/callbacks.

## Important APIs, types, and functions

- `sdw_intel_cnl_hw_ops` is the exported ops table consumed through `struct sdw_intel_link_res::hw_ops`.
- Register helpers `intel_wait_bit()`, `intel_set_bit()`, and `intel_clear_bit()` poll MMIO status during link power transitions.
- Debugfs helpers expose `intel-registers`, `intel-m-datamode`, and `intel-s-datamode`; the data mode files taint the kernel because they alter runtime bus parameters behind normal policy.
- SHIM functions `intel_shim_init()`, `intel_shim_glue_to_master_ip()`, `intel_shim_master_ip_to_glue()`, `intel_shim_wake()`, and `intel_shim_check_wake()` own glue/Master-IP handoff and wake status.
- `intel_link_power_up()` and `intel_link_power_down()` coordinate shared SHIM state through `shim_lock`, `shim_mask`, `link_mask`, SyncPRD, SyncCPU, SPA/CPA, and optional MLCS clock source programming.
- `intel_shim_sync_arm()`, `intel_shim_sync_go[_unlocked]()`, and `intel_check_cmdsync_unlocked()` implement multi-link command synchronization.
- PDI routines read `PCMSCAP`, channel capability, configure SHIM `PCMSYCHM`, and configure ALH `STRMZCFG`.
- ASoC DAI callbacks are `intel_hw_params()`, `intel_prepare()`, `intel_hw_free()`, `intel_trigger()`, plus stream set/get glue.
- `intel_register_dai()` initializes Cadence PDI descriptors and registers `soundwire` component DAIs.

## Control flow

Startup arrives through `intel_auxdevice.c`, which calls `sdw_intel_link_power_up()` and `sdw_intel_register_dai()`. Power-up locks the shared SHIM, programs SyncPRD based on firmware `mclk_freq`, powers all enabled links when this is the first active link, switches the current link from glue to master IP control, marks `cdns.link_up`, and initializes CTMCTL.

For PCM setup, ASoC calls `.hw_params`. The driver allocates a Cadence PDI matching channel count/direction/DAI id, programs SHIM and ALH stream IDs, configures the Cadence stream, informs the parent DSP via `res->ops->params_stream`, then adds the master port to the SoundWire stream. Resume and xrun handling reenter through `.prepare`; only the suspended path reprograms SHIM/ALH/Cadence state. `.hw_free` removes the master from the SoundWire stream, calls the parent `free_stream`, and clears the PDI pointer.

Multi-link bank switching is split between pre-bank `CMDSYNC` arming and post-bank `SYNCGO`. The common stream layer invokes these through `sdw_master_ops`, and this file uses the SHIM sync register to trigger one synchronized switch for all links.

## State and persistence behavior

Software state lives mainly in `struct sdw_intel`, its Cadence child, and shared `link_res` fields. `startup_done` is managed elsewhere, while this file mutates `cdns.link_up`, DAI runtime `paused`/`suspended`/`pdi`, bus data-mode parameters through debugfs, and shared `*shim_mask`. Persistent hardware state is in SHIM, ALH, and Cadence registers and survives until link reset/power-down or reconfiguration. The code relies on `shim_lock` for all shared SHIM power/sync/wake operations.

## Dependencies and integration points

This file depends on Cadence SoundWire helpers (`sdw_cdns_*`), the common SoundWire stream API, Intel register definitions, ASoC DAI/component APIs, PM runtime for component probing, and parent Intel audio/DSP callbacks supplied through `struct sdw_intel_ops`. It integrates with `intel_auxdevice.c` through `sdw_intel_cnl_hw_ops`, with `intel_bus_common.c` for bus start/stop and bank-switch routines, and with debugfs when enabled.

## Risks and edge cases

- Incorrect `mclk_freq` or MLCS reporting can reject link power-up or select the wrong SyncPRD/clock source.
- `shim_mask` is shared across links; unbalanced power-up/down calls are detected but can still leave link state degraded.
- PDI number 2 is hard-coded to 8 channels because hardware reports one channel; this is generation-specific and easy to carry incorrectly.
- Debugfs data-mode overrides intentionally bypass normal policy and taint the kernel.
- Error unwinding in `.hw_params` relies on higher layers to clean up partially configured PDI/stream state if DSP callback or stream-add fails.
- Multi-link sync requires `shim_lock` ordering and correct CMDSYNC handling; mistakes can deadlock or switch banks unsafely across links.

## Test signals

Useful signals include module build with `CONFIG_DEBUG_FS` on/off, probe/startup on CNL-family hardware, runtime PM suspend/resume with active and paused streams, ASoC PCM open/prepare/hw_free paths, multi-link playback/capture with synchronized bank switch, debugfs register dump reads, and injected failures in parent `params_stream`/`free_stream`. Hardware traces should confirm SHIM LCTL CPA/SPA, SYNC, CTMCTL, PCMSYCHM, and ALH stream config values.
