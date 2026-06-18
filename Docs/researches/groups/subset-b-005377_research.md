# subset-b-005377 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel.h -->
# sources/distributed-fs/ceph-client/drivers/soundwire/intel.h

## Purpose

`intel.h` is the local Intel SoundWire link header shared by the Intel init, auxiliary-device, classic SHIM, ACE2.x, debugfs, and common bus files. It defines the per-link resource contract, runtime Intel wrapper, BPT context, vendor-specific property storage, PDI type enum, MMIO helper functions, and inline dispatch wrappers for platform-specific hardware ops.

## Important APIs, types, and functions

- `struct sdw_intel_link_res` carries parent-provided resources: hardware ops, MMIO bases, SHIM/ALH/SHIM-VS pointers, IRQ, parent callbacks, locks, masks, clock-stop quirks, link mask, Cadence pointer, link-list node, and HDA bus pointer.
- `struct sdw_intel_bpt` stores HDA BPT TX/RX stream handles, DMA buffers, and computed transfer sizes.
- `struct sdw_intel` embeds `struct sdw_cdns`, link id, resource pointer, startup flag, BPT context, and optional debugfs root.
- `struct sdw_intel_prop` holds Intel-specific firmware properties used by ACE2.x vendor-specific ACTMCTL programming.
- Inline register helpers wrap `readl/writel/readw/writew`.
- `SDW_INTEL_CHECK_OPS()` and `SDW_INTEL_OPS()` implement guarded hardware-op dispatch.
- Inline wrappers such as `sdw_intel_link_power_up()`, `sdw_intel_start_bus()`, `sdw_intel_register_dai()`, `sdw_intel_sync_go()`, and `sdw_intel_get_link_count()` hide generation differences from call sites.
- Common bus prototypes expose `intel_start_bus()`, resume variants, `intel_stop_bus()`, and common bank-switch callbacks.

## Control flow

The header itself has no runtime control path, but it defines the indirection model. `intel_init.c` fills `sdw_intel_link_res` for each auxiliary link. `intel_auxdevice.c` converts that resource into `struct sdw_intel` plus Cadence bus state, then all runtime operations call the inline wrappers. The wrappers check whether a generation-specific operation exists and either invoke it or return a default such as `-ENOTSUPP`, `false`, or four links for older hardware.

## State and persistence behavior

The header defines the state layout but does not mutate state. Important lifetimes are split: `sdw_intel_link_res` belongs to the auxiliary link device, `sdw_intel` is device-managed under the auxiliary driver, BPT DMA resources are opened/closed per BPT transaction, and the shared SHIM mask/lock are owned by the controller context. Hardware state is accessed through MMIO pointers and HDA multi-link helpers selected by the ops table.

## Dependencies and integration points

The header depends on SoundWire public types, Cadence local types, HDA bus forward declaration, and Intel public resource/callback definitions from `linux/soundwire/sdw_intel.h`. It is the main integration seam between older CNL-style ops in `intel.c`, LunarLake/ACE2.x ops in `intel_ace2x.c`, common bus handling in `intel_bus_common.c`, auxiliary-device binding in `intel_auxdevice.c`, and controller enumeration in `intel_init.c`.

## Risks and edge cases

- Inline wrappers return `-ENOTSUPP` for missing ops; callers must distinguish unsupported hardware from transient failures.
- The default link count is four, which is correct for older generations but unsafe if used accidentally on newer hardware without a real `get_link_count`.
- `sdw_intel_link_res` combines shared and per-link pointers. Incorrect initialization of `shim_lock`, `shim_mask`, `link_mask`, or `hbus` can corrupt shared power management.
- ACE2.x and older hardware share the same `struct sdw_intel`; any future field additions must preserve both code paths.

## Test signals

Build both classic Intel and ACE2.x configurations, with and without `CONFIG_DEBUG_FS`. Static checks should ensure every wrapper has a corresponding ops field and every ops user handles unsupported returns. Probe tests should confirm resources are populated correctly for non-extended and extended (`res->ext`) controller layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_ace2x.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/intel_ace2x.c

## Purpose

`intel_ace2x.c` implements Intel ACE2.x/LunarLake SoundWire hardware operations exported as `sdw_intel_lnl_hw_ops`. It reuses the common Intel/Cadence bus management layer but replaces SHIM power, sync, wake, PDI, DAI, and BPT behavior with HDA multi-link (`hda-mlink`) and HDA SoundWire BPT helpers.

## Important APIs, types, and functions

- `sdw_intel_lnl_hw_ops` is the exported ACE2.x ops table.
- BPT helpers `intel_ace2x_bpt_send_async()` and `intel_ace2x_bpt_wait()` implement the bus `bpt_send_async`/`bpt_wait` path.
- `intel_ace2x_bpt_open_stream()` allocates a BPT `sdw_stream_runtime`, adds slave DP0 and two master PDIs, prepares the stream, computes Cadence BPT frame/buffer sizes, opens HDA BPT DMA, and formats TX buffers.
- `intel_ace2x_bpt_close_stream()` closes HDA BPT DMA, deprepares/removes stream participants, and clears `bus.bpt_stream`.
- Vendor SHIM helpers configure VS ACTMCTL from Intel firmware properties, set MLCS clock source, and map wake handling to HDaudio `WAKEEN`/`STATESTS` using `lsdiid`.
- `intel_link_power_up()` and `intel_link_power_down()` call `hdac_bus_eml_sdw_power_up/down_unlocked()` and enable/disable HDA multi-link interrupts when the first/last SoundWire link changes state.
- Sync helpers call `hdac_bus_eml_sdw_sync_arm_unlocked()`, `sync_go_unlocked()`, and `check_cmdsync_unlocked()`.
- ACE2.x DAI callbacks mirror older Intel DAI operations but delegate SHIM programming to callback functions and call an optional parent trigger callback.
- `intel_program_sdi()` programs the link-specific wake device id, and `intel_get_link_count()` queries HDA multi-link topology.

## Control flow

Normal startup enters through `intel_auxdevice.c`. The common startup path calls `sdw_intel_link_power_up()`, which for ACE2.x powers the HDA multi-link SoundWire endpoint, selects a clock source from firmware `mclk_freq`, programs shared SyncPRD on first link, enables HDA multi-link interrupts, marks the link up, and initializes Intel vendor SHIM ACTMCTL.

PCM `.hw_params` allocates a Cadence PDI, calculates the same Intel ALH id scheme used by previous generations, configures the Cadence stream, notifies the parent DSP with `params_stream`, and adds a master port to the common SoundWire stream. `.prepare` always reissues `params_stream`, and when the DAI was suspended it also reconfigures Cadence stream state. `.trigger` first gives the parent driver a chance to program HDA DMA/firmware IPC, then updates local paused/suspended flags.

BPT flow is stricter. `bpt_send_async` rejects transfers below 16 bytes, opens the BPT stream, starts HDA TX/RX DMA, then enables the SoundWire stream. `bpt_wait` waits for HDA completion, disables the stream, validates write or read responses in the RX DMA buffer, and closes the stream. Read commands add padded fake frames to satisfy DMA alignment and minimum PDI1 read size.

## State and persistence behavior

Runtime state includes `sdw->bpt_ctx`, `cdns->bus.bpt_stream`, HDA DMA buffers/streams, Cadence PDI allocation, DAI runtime flags, and shared `shim_mask`. Hardware state persists in HDA multi-link power/interrupt registers, ACE2.x SHIM/VS registers, Cadence MCP registers, and HDA BPT DMA resources until explicitly disabled or reset. BPT stream state is intended to be single-use; stream allocation fails if another BPT stream exists or audio streams are active on that bus.

## Dependencies and integration points

This file depends on `sound/hda-mlink.h`, `sound/hda-sdw-bpt.h`, HDA register access, Cadence SoundWire helpers, the common SoundWire stream state machine, ASoC DAI APIs, Intel resource callbacks, and firmware properties parsed in `intel_auxdevice.c`. It imports `SND_SOC_SOF_HDA_MLINK` and `SND_SOC_SOF_INTEL_HDA_SDW_BPT` namespaces.

## Risks and edge cases

- BPT resource unwinding spans SoundWire streams, Cadence PDIs, HDA DMA, and slave/master attachments; missing an unwind step can leave `bpt_stream` stuck or DMA buffers open.
- The minimum BPT message length, read padding, alignment, and fake-frame calculations are hardware-sensitive.
- `intel_shim_check_wake()` resumes unconditionally, so wake handling depends on disabling WAKEEN quickly enough to avoid interrupt storms.
- `intel_pdi_init()` sets `pcm_out` from the ISS field, which should be validated against ACE2.x documentation because it differs from classic PCMSCAP handling.
- Parent `trigger`, `params_stream`, and `free_stream` callbacks become part of the PCM critical path.
- Shared HDA multi-link interrupt enablement depends on the global `shim_mask`; imbalance across links can affect all SoundWire links.

## Test signals

Run compile tests with HDA multi-link and BPT namespaces enabled. On ACE2.x hardware, validate link power-up/down, wake resume, link-count bounds, multi-link bank switching, PCM playback/capture including suspend/resume and pause-suspend corner cases, and BPT read/write paths with minimum, aligned, and multi-section messages. DMA buffer validation helpers should be exercised under injected timeout/error responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_ace2x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_ace2x_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/intel_ace2x_debugfs.c

## Purpose

`intel_ace2x_debugfs.c` provides debugfs support for Intel ACE2.x SoundWire links. It exposes ACE2.x SHIM, vendor-specific SHIM, optional microphone privacy, and Cadence debug registers, plus writable debugfs knobs for master/slave data mode overrides.

## Important APIs, types, and functions

- `intel_ace2x_debugfs_init()` creates `intel-sdw` under the bus debugfs root.
- `intel_ace2x_debugfs_exit()` removes the debugfs subtree.
- `intel_reg_show()` formats selected SHIM2, PCMSYCH, vendor clock, wake, IOCTL, ACTMCTL, and optional PVCCS registers.
- `intel_set_m_datamode()` and `intel_set_s_datamode()` validate data-mode values, taint the kernel, and modify `bus->params.m_data_mode` or `s_data_mode`.
- `intel_sprintf()` centralizes 16-bit vs 32-bit register reads into the fixed 2-page buffer.

## Control flow

The ACE2.x hardware ops table points debugfs init/exit at this file. During link startup, the auxiliary driver calls `sdw_intel_debugfs_init()`, which dispatches to `intel_ace2x_debugfs_init()`. Users reading `intel-registers` get a snapshot of the selected hardware registers. Users writing data-mode files alter the in-memory bus parameter used by later stream preparation/programming.

## State and persistence behavior

The debugfs directory pointer is stored in `sdw->debugfs`. Register reads do not alter hardware state. Data-mode writes mutate `struct sdw_bus_params` and persist until overwritten, bus reset/reinit, or driver teardown. Because those writes bypass normal configuration, they intentionally call `add_taint(TAINT_USER, LOCKDEP_STILL_OK)`.

## Dependencies and integration points

This file depends on `CONFIG_DEBUG_FS`, Intel register definitions, Cadence debugfs helpers, and `struct sdw_intel`. Its public declarations are conditionally provided by `intel.h`; when debugfs is disabled, inline no-op stubs replace these functions.

## Risks and edge cases

- The register dump uses a fixed two-page buffer; adding more registers without checking remaining space can truncate output.
- Writable data-mode knobs can create configurations not expected by stream code or hardware.
- Debugfs accesses assume link resources and MMIO mappings remain valid for the directory lifetime.
- The number of PCMSYCH registers dumped is based on BSS from PCMSCAP; if hardware reports inconsistent capability, the dump can omit useful registers.

## Test signals

Build with `CONFIG_DEBUG_FS=y` and `n`. On ACE2.x hardware, confirm `intel-sdw/intel-registers` produces SHIM and VS sections, PVCCS appears only when `mic_privacy` is true, data-mode writes reject values above `SDW_PORT_DATA_MODE_STATIC_1`, and debugfs removal during driver unload leaves no stale dentries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_ace2x_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_auxdevice.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/intel_auxdevice.c

## Purpose

`intel_auxdevice.c` is the auxiliary-bus Intel SoundWire link driver. It binds each `soundwire_intel.link` auxiliary device into a Cadence-backed SoundWire master, reads generic and Intel-specific firmware properties, handles device-number allocation and wake-capable peripherals, starts DAIs and the bus, processes wake events, and owns runtime/system PM policy for Intel links.

## Important APIs, types, and functions

- Module parameters `sdw_md_flags` and `sdw_mclk_divider` control per-link PM/multi-link behavior and clock workarounds.
- `wake_capable_list`, `is_wake_capable()`, `intel_get_device_num_ida()`, and `intel_put_device_num_ida()` reserve higher device numbers for wake-capable parts.
- `sdw_master_read_intel_prop()` reads `intel-sdw-ip-clock`, `intel-quirk-mask`, and Intel timing properties from `mipi-sdw-link-N-subproperties`.
- `sdw_intel_ops` is the master ops table wiring Cadence transfers, bank-switch callbacks, device-number allocation, BPT hooks, DMI ADR override, and bus config.
- `intel_link_probe()` creates `struct sdw_intel`, initializes Cadence state, validates link count, calls `sdw_cdns_probe()`, and registers the SoundWire master.
- `intel_link_startup()` powers the link, registers DAIs, enables debugfs/runtime PM, starts the bus, applies clock-stop quirks, and marks `startup_done`.
- PM callbacks `intel_pm_prepare()`, `intel_suspend()`, `intel_suspend_runtime()`, `intel_resume()`, and `intel_resume_runtime()` implement Intel clock-stop, teardown, bus-reset, and full resume flows.
- `intel_link_process_wakeen_event()` handles shared WAKEEN events by disabling wake and requesting link resume.

## Control flow

Probe is two-stage. `intel_init.c` creates the auxiliary device, then this driver probes it and registers a SoundWire master with properties but does not necessarily start the hardware bus. Later, `sdw_intel_startup()` calls `intel_link_startup()` for enabled links after the Intel audio DSP is powered. Startup resolves module flags, enables multi-link synchronization if allowed, powers the link through generation-specific hw ops, registers DAIs, enables PM, starts the Cadence bus, applies no-clock-stop quirks, and idles runtime PM.

Runtime PM suspend chooses one of three flows from `clock_stop_quirks`: teardown powers the bus down without clock stop; bus reset requests clock stop plus reset on resume; no quirks uses normal clock stop and wake enable. Runtime resume disables wake, powers up if needed, clears slave status for reset/teardown paths, and restarts the bus using the matching common bus helper. System suspend disables runtime PM to avoid races and either handles an already suspended link or stops the bus without wake-based clock stop.

Wake events are dispatched from the parent context across link devices. A link ignores wake if disabled or not started, checks generation wake status, disables WAKEEN immediately, and requests runtime resume.

## State and persistence behavior

State includes `sdw->startup_done`, bus properties, Cadence bus lists, DAI runtime arrays, runtime PM state, `intel_peripheral_ida`, `bus->assigned`, and shared wake/device-number policy. Firmware-derived Intel properties are allocated with devm and stored in `bus->vendor_specific_prop`. PM transitions persist through hardware link power, clock-stop, WAKEEN, slave status, and Cadence bus reset state.

## Dependencies and integration points

This driver depends on the Linux auxiliary bus, Cadence SoundWire controller helpers, generic SoundWire bus/master APIs, DMI ADR override, PM runtime, ASoC component registration through generation ops, Intel public resource callbacks, and firmware DisCo properties. It is the central bridge between `intel_init.c`, `intel.c`/`intel_ace2x.c`, `intel_bus_common.c`, and the generic SoundWire bus core.

## Risks and edge cases

- `intel_prop_read()` ignores the return from `sdw_master_read_intel_prop()`, so missing Intel-specific properties may be reported but not fatal.
- Wake-capable parts rely on both firmware `wake_capable` and a hard-coded ID list; stale lists can assign the wrong device-number range.
- Runtime PM reference handling differs when `clock_stop_quirks` is zero versus nonzero and when module flags disable PM.
- System suspend handles failures leniently in `.prepare` to avoid blocking suspend, so recovery depends on resume paths.
- The PM paths assume parent PCI/DSP power sequencing makes SHIM/HDA registers accessible at the right time.
- Bus restart paths must match the exact suspend mode or slaves may retain stale status/device numbers.

## Test signals

Test probe with enabled, disabled, and out-of-range link ids; firmware with and without Intel subproperties; wake-capable and non-wake-capable peripherals; module flags disabling PM, idle, clock stop, and multi-link; runtime suspend/resume for teardown, bus-reset, and clock-stop modes; wake IRQ flooding; system suspend while a stream is paused; and cleanup/unbind while children are runtime suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_auxdevice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_auxdevice.h -->
# sources/distributed-fs/ceph-client/drivers/soundwire/intel_auxdevice.h

## Purpose

`intel_auxdevice.h` is the small local contract between Intel SoundWire controller setup and the auxiliary link driver. It declares link startup, wake processing, child resume, and the auxiliary-device container that carries per-link resources.

## Important APIs, types, and functions

- `intel_link_startup()` starts a probed auxiliary link after parent audio power is available.
- `intel_link_process_wakeen_event()` asks an auxiliary link to process a shared wake event.
- `intel_resume_child_device()` is used during cleanup/system prepare to resume probed child SoundWire slaves.
- `struct sdw_intel_link_dev` embeds `struct auxiliary_device` and `struct sdw_intel_link_res`.
- `auxiliary_dev_to_sdw_intel_link_dev()` converts an auxiliary device to the Intel link container.

## Control flow

`intel_init.c` allocates `sdw_intel_link_dev`, fills the embedded `link_res`, and registers the auxiliary device. `intel_auxdevice.c` receives that device in probe, accesses the resource through the container macro, and later services startup/wake/resume calls exported through this header.

## State and persistence behavior

The header defines ownership shape only. `sdw_intel_link_dev` lives for the auxiliary device lifetime and is freed by the release callback in `intel_init.c`. Its embedded `link_res` persists across probe, startup, PM, wake, and cleanup.

## Dependencies and integration points

It depends on Linux auxiliary-device types and the Intel link resource type from `intel.h`. Its only users in this subset are `intel_init.c` and `intel_auxdevice.c`.

## Risks and edge cases

- The container macro assumes the auxiliary device is embedded exactly as declared.
- The header does not include explicit type forward declarations; include order must provide `struct auxiliary_device`, `struct device`, and `struct sdw_intel_link_res`.
- Lifetime correctness depends on auxiliary device delete/uninit ordering and the release callback.

## Test signals

Build coverage should catch include-order problems. Probe/unbind tests should verify `sdw_intel_link_dev` is released exactly once and no caller uses the link resource after auxiliary uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_auxdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_bus_common.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/intel_bus_common.c

## Purpose

`intel_bus_common.c` contains Intel bus lifecycle and bank-switch helpers shared by classic Intel and ACE2.x hardware ops. It coordinates Cadence soft reset/init, config update, interrupt enable, clock stop/restart, delayed enumeration, slave status clearing, link power-down, wake enable, and multi-link sync pre/post callbacks.

## Important APIs, types, and functions

- `intel_start_bus()` performs first startup after link power-up.
- `intel_start_bus_after_reset()` restarts after runtime resume with bus reset semantics and handles the clock-stop0 preservation case.
- `intel_check_clock_stop()` validates that Cadence reported clock-stop state.
- `intel_start_bus_after_clock_stop()` restarts from normal clock stop.
- `intel_stop_bus()` cancels enumeration, optionally enters clock stop, disables Cadence interrupts, powers down the link, and programs SHIM wake.
- `intel_pre_bank_switch()` and `intel_post_bank_switch()` arm and trigger hardware synchronized bank switches for multi-link streams.

## Control flow

Startup soft-resets Cadence, arms hardware sync for multi-link, initializes Cadence, issues config update, optionally triggers sync go, waits for config update to clear, enables interrupts, exits reset, checks self-clearing bits, and schedules delayed enumeration. Resume-after-reset is similar but either reinitializes from a non-clock-stop0 state or simply enables interrupts for preserved clock-stop0, then restarts the Cadence clock and schedules enumeration.

Stop flow cancels attach work first. If clock stop is requested, it asks Cadence to stop the clock and sets `wake_enable` only on success. It then disables interrupts, powers down the link through generation ops, and programs wake enable/disable based on whether clock stop succeeded.

Bank-switch callbacks are no-ops unless `bus->multi_link` is true. Pre-bank arms sync. Post-bank takes the shared SHIM lock and issues `SYNCGO` only if any CMDSYNC bit is still armed, so only the first master in the stream triggers the synchronized switch.

## State and persistence behavior

The file mutates Cadence bus state, interrupt state, delayed work, slave attachment status, clock-stop state, and hardware sync bits. It relies on `bus->multi_link`, `bus->hw_sync_min_links`, and generation-specific sync ops. Hardware state persists in Cadence MCP registers and Intel SHIM/HDA sync/wake state.

## Dependencies and integration points

It depends on Cadence helpers, generic SoundWire bus helpers (`sdw_clear_slave_status()`), Intel inline op wrappers, and common delayed enumeration work. It is called from Intel hardware ops tables and PM paths in `intel_auxdevice.c`.

## Risks and edge cases

- Error paths after partial startup may leave interrupts or config state partially enabled; callers must unwind power and PM.
- `intel_stop_bus()` returns before wake programming if interrupt disable or power-down fails.
- Resume-after-reset must correctly identify clock-stop0 preservation; clearing slave status unnecessarily can force avoidable reenumeration, while failing to clear can leave stale devices.
- Multi-link post-bank locking assumes all involved links share compatible `shim_lock` ordering.
- Delayed enumeration timing is fixed at 100 ms, which can be sensitive to slow peripherals.

## Test signals

Validate startup, stop with and without clock stop, resume after teardown, resume after bus reset, resume after normal clock stop, multi-link bank switching, single-link no-op bank switch, and failure injection for Cadence init/config-update/interrupt/clock operations. Check delayed work cancellation on stop and scheduling on every successful start path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_bus_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_init.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/intel_init.c

## Purpose

`intel_init.c` is the Intel SoundWire controller initialization library used by the parent Intel audio driver. It scans controller resources, creates one auxiliary link device per enabled SoundWire link, collects link Cadence buses and slaves, starts links after parent DSP power-up, dispatches shared IRQ and wake events, and cleans up all auxiliary devices.

## Important APIs, types, and functions

- `sdw_intel_probe()` allocates a `struct sdw_intel_ctx` and registers auxiliary link devices.
- `sdw_intel_startup()` starts all enabled links by calling `intel_link_startup()`.
- `sdw_intel_exit()` resumes children, unregisters auxiliary devices, and frees context arrays.
- `sdw_intel_thread()` is the exported threaded IRQ dispatcher that calls `sdw_cdns_irq()` for each link in `ctx->link_list`.
- `sdw_intel_process_wakeen_event()` forwards a shared wake event to every enabled link.
- `intel_link_dev_register()` builds each `sdw_intel_link_dev`, maps classic versus extended register layouts, fills `link_res`, and registers the auxiliary device.
- `sdw_intel_probe_controller()` owns controller-level discovery, context allocation, link mask handling, link list creation, and flattened peripheral array construction.

## Control flow

The parent driver calls `sdw_intel_probe()` after ACPI scan and passes `sdw_intel_res`. The controller probe verifies ACPI handle/count, allocates `ctx` and link-device pointer array, initializes shared SHIM lock and link mask, then registers auxiliary devices for enabled links. Each auxiliary device probes separately in `intel_auxdevice.c`; after add, this file retrieves the Cadence pointer from auxiliary driver data, adds the link to `ctx->link_list`, and counts slaves on the bus. It then builds a flex-array of all slave pointers for parent use.

Startup is a second phase. `sdw_intel_startup()` iterates enabled links, calls `intel_link_startup()`, and holds a parent runtime PM reference for links without clock-stop quirks. Exit first resumes child devices for each bus to avoid tearing down suspended devices, then disables PM, unregisters auxiliary devices, drops parent references where applicable, frees peripherals, link array, and context.

## State and persistence behavior

`struct sdw_intel_ctx` stores link count, link mask, MMIO base metadata, ACPI handle, shared SHIM mask/lock, link list, per-link auxiliary pointers, and a flattened peripherals array. The auxiliary device owns each `sdw_intel_link_res`. The controller-level `shim_mask` tracks powered links across all auxiliary drivers. No persistent on-disk state exists; hardware state is managed by the per-link driver.

## Dependencies and integration points

This file depends on ACPI, Linux auxiliary bus, PM runtime, Cadence IRQ handling, and Intel link driver entry points declared in `intel_auxdevice.h`. Its exported namespace is `SOUNDWIRE_INTEL_INIT`, consumed by parent Intel audio/SOF code.

## Risks and edge cases

- Probe cannot use devm allocation because it may run from a workqueue; all error paths must manually free link arrays and auxiliary devices.
- If auxiliary probe fails to set driver data, the error path adjusts the loop index to unregister the just-created device; this is delicate.
- Cleanup assumes enabled links have valid `ctx->ldev[i]` pointers.
- `sdw_intel_startup_controller()` does not aggregate or check `intel_link_startup()` return values, so startup failures may be hidden.
- Peripheral array size is computed from slaves visible immediately after auxiliary probe; delayed enumeration later can make the snapshot stale.
- IRQ dispatch walks all registered links and calls Cadence IRQ even if one link has problems.

## Test signals

Test ACPI missing handle, zero link count, sparse link masks, auxiliary add/probe failure, startup with a disabled link, cleanup after partial probe, IRQ handling with multiple links, wake forwarding, and exit while children are runtime suspended. Static review should focus on manual lifetime/error paths and the ignored startup return value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/intel_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/irq.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/irq.c

## Purpose

`irq.c` implements optional IRQ-domain support for SoundWire slave interrupt mapping. It creates a linear IRQ domain per bus, maps slave hardware indices to nested Linux IRQs, and registers device-managed cleanup for slave mappings.

## Important APIs, types, and functions

- `sdw_irq_create()` initializes `bus->irq_chip.name` and creates a linear irqdomain sized to `SDW_FW_MAX_DEVICES`.
- `sdw_irq_delete()` removes the bus IRQ domain.
- `sdw_irq_create_mapping()` maps `slave->index` to `slave->irq` and registers `sdw_irq_dispose_mapping()` as a devm cleanup action.
- `sdw_irq_map()` sets irq chip data to the bus, assigns `bus->irq_chip`, marks the IRQ nested-threaded, and disables probing.

## Control flow

When a SoundWire bus is registered with IRQ-domain support, the bus creates its domain. When a slave is discovered, the core calls `sdw_irq_create_mapping()`, which creates a virtual IRQ from the slave index. On slave device removal, the devm action disposes the mapping. Bus teardown removes the entire domain.

## State and persistence behavior

State is held in `bus->domain`, `bus->irq_chip`, and each `slave->irq`. Mappings live for the slave device lifetime and are cleaned up through devm. No hardware state is programmed here; actual interrupt status and dispatch are handled by bus/controller code.

## Dependencies and integration points

The file depends on `CONFIG_IRQ_DOMAIN`, Linux irqdomain APIs, device-managed actions, and SoundWire bus/slave structures. It integrates with the SoundWire bus core that creates domains and maps slaves, and with slave drivers that request/use nested IRQs.

## Risks and edge cases

- A failed `irq_create_mapping()` only warns; drivers must tolerate `slave->irq == 0`.
- The domain is linear and sized to firmware max devices, so `slave->index` must be stable and in range.
- `sdw_irq_delete()` assumes a valid domain pointer.
- The irq chip callbacks must be populated elsewhere in `bus->irq_chip`; this file only assigns chip identity.

## Test signals

Build with `CONFIG_IRQ_DOMAIN` enabled. Validate domain creation/removal, slave mapping/disposal, failure of mapping allocation, and nested IRQ delivery through a slave driver. KASAN/devm tests should confirm no mapping survives slave removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/irq.h -->
# sources/distributed-fs/ceph-client/drivers/soundwire/irq.h

## Purpose

`irq.h` declares the local SoundWire IRQ-domain helpers and provides no-op inline stubs when IRQ domains are disabled. It lets bus code call IRQ setup uniformly across configurations.

## Important APIs, types, and functions

- `sdw_irq_create()` creates a bus IRQ domain when `CONFIG_IRQ_DOMAIN` is enabled and otherwise returns success.
- `sdw_irq_delete()` removes a bus IRQ domain or does nothing in stub builds.
- `sdw_irq_create_mapping()` maps a slave IRQ or does nothing in stub builds.

## Control flow

Callers include this header and invoke the helpers during bus/slave setup and teardown. The preprocessor selects real declarations or no-op definitions based on `IS_ENABLED(CONFIG_IRQ_DOMAIN)`.

## State and persistence behavior

The header itself has no state. In stub builds, no `bus->domain` or `slave->irq` state is created by these helpers.

## Dependencies and integration points

It depends on SoundWire public types and firmware-node types. It is paired with `irq.c` and used by the SoundWire bus core.

## Risks and edge cases

- Stub builds silently skip IRQ mapping; slave drivers must not assume an IRQ exists.
- Call sites must be valid in both compiled-in and no-op configurations.
- The header uses `IS_ENABLED`, so the inline path also applies when IRQ domain support is a module-incompatible absence.

## Test signals

Compile with IRQ domain support enabled and disabled. In disabled builds, verify bus registration still succeeds and slave drivers handle absent IRQs gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/master.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/master.c

## Purpose

`master.c` creates the Linux device representation for a SoundWire master bus and exposes master DisCo properties through sysfs. It also enables runtime PM on the master device so the master can autosuspend when no children keep the bus active.

## Important APIs, types, and functions

- `sdw_master_device_add()` allocates and registers `struct sdw_master_device`.
- `sdw_master_device_del()` disables runtime PM and unregisters the master device.
- `sdw_master_type` describes the device type, release callback, and runtime PM operations.
- Sysfs attributes expose `revision`, `clk_stop_modes`, `max_clk_freq`, `default_row`, `default_col`, `default_frame_rate`, `dynamic_frame`, `err_threshold`, `clock_frequencies`, and `clock_gears`.
- `master_dev_pm` uses generic runtime suspend/resume callbacks.

## Control flow

The controller driver calls `sdw_master_device_add()` after initializing an `sdw_bus`. The function allocates the master device, sets bus/type/parent/groups/fwnode/DMA mask, names it `sdw-master-controller-link`, registers it, stores shortcuts in `bus->dev` and `bus->md`, and enables autosuspend with a 3 second delay. Deletion disables runtime PM and unregisters the device; the release callback frees the allocation.

## State and persistence behavior

The master device owns sysfs-visible property state indirectly through `md->bus->prop`. Runtime PM state is stored in the device core. No hardware registers are touched here; persistence is limited to the registered device lifetime and property values filled by controller property-reading callbacks.

## Dependencies and integration points

It depends on the SoundWire bus type, `struct sdw_master_device`, Linux device/sysfs APIs, ACPI/fwnode plumbing, and PM runtime. Controllers such as Intel and Qualcomm call this through `sdw_bus_master_add()` and delete through `sdw_bus_master_delete()`.

## Risks and edge cases

- Property sysfs uses `sprintf` and assumes arrays and counts in `bus->prop` are initialized correctly.
- On `device_register()` failure, ownership transfers to `put_device()` and the caller must not free `md`.
- Runtime PM autosuspend behavior depends on child devices becoming active when attached; buses with no attached slaves autosuspend after the delay.
- `sdw_master_device_del()` assumes `bus->md` and `bus->dev` are valid.

## Test signals

Validate master device names for multiple controller/link ids, sysfs attributes after DisCo property parsing, add failure cleanup, runtime PM autosuspend with no slaves, active child preventing master suspend, and clean deletion during controller unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/mipi_disco.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/mipi_disco.c

## Purpose

`mipi_disco.c` reads MIPI SoundWire DisCo firmware properties for masters and slaves from generic device properties/fwnodes. It populates bus, slave, DP0, DPn, lane mapping, and capability structures used by enumeration, stream setup, sysfs, and controller-specific policy.

## Important APIs, types, and functions

- `sdw_master_read_prop()` reads master revision, clock-stop modes, clock frequencies/gears, default frame rate/row/col, dynamic frame support, and error threshold.
- `sdw_slave_read_prop()` reads slave capabilities, source/sink port lists, SDCA interrupt register list, commit register support, DP0 properties, DPn source/sink properties, and lane mappings.
- `sdw_slave_read_lane_mapping()` parses `mipi-sdw-lane-N-mapping` strings into `slave->prop.lane_maps`.
- Internal helpers read firmware booleans encoded as u8 properties, DP0 properties, and per-port DPn properties.

## Control flow

Controller or bus code calls `sdw_master_read_prop()` during master registration/property read. It locates `mipi-sdw-link-N-subproperties`, reads optional properties, allocates arrays for clock frequencies/gears, derives `max_clk_freq` if missing, and releases the fwnode.

Slave drivers or bus code call `sdw_slave_read_prop()` after a slave device is created. The function reads top-level slave capabilities, optionally reads `mipi-sdw-dp-0-subproperties`, allocates arrays sized by source/sink port bit counts, reads each named `mipi-sdw-dp-N-source/sink-subproperties` child, and finally parses lane mappings.

## State and persistence behavior

The file fills `bus->prop` and `slave->prop` structures. Variable-sized arrays are devm-allocated against the bus device or slave device, so they persist for the relevant device lifetime. There is no hardware state or on-disk state.

## Dependencies and integration points

It depends on Linux firmware property APIs, SoundWire public structures, and the local bus header. The resulting properties feed sysfs (`master.c`, `sysfs_slave.c`), stream validation/configuration (`stream.c`), Intel/Qualcomm policy, and slave driver callbacks.

## Risks and edge cases

- Several helper calls ignore return values, especially DP0/DPn reads, so missing or malformed properties can leave zero/default fields without aborting.
- Boolean properties are read as u8 arrays rather than standard boolean presence, matching DisCo encoding but sensitive to firmware representation.
- `sdw_slave_read_dpn()` has a `count` parameter that is not used to bound writes; correctness depends on the port bitmask and allocation count matching.
- Some `fwnode_handle_put()` paths are missing on early return after read errors, which is a leak risk.
- `wake_capable` is inverted from `mipi-sdw-wake-up-unavailable`, which is easy to misread.
- Lane mapping parses the final character as a decimal manager lane and does not model peripheral-link letters described in the comment.

## Test signals

Use ACPI/DT fixtures with full, partial, and malformed DisCo properties. Verify clock frequency/gears allocation, max clock derivation, DP0 sysfs visibility, source/sink port property arrays, lane mappings, wake capability inversion, and error behavior when child nodes are missing. Static analysis should check fwnode put coverage and array bounds relative to port bit counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/mipi_disco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/qcom.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/qcom.c

## Purpose

`qcom.c` is the Qualcomm SoundWire manager platform driver. It supports multiple hardware register layouts, initializes the controller, handles command FIFO reads/writes, auto-enumeration, interrupts, runtime PM and clock stop, master port programming, and ASoC PDM DAI registration.

## Important APIs, types, and functions

- `struct qcom_swrm_ctrl` contains the `sdw_bus`, MMIO/regmap accessors, layout table, clocks/resets, IRQs, completions, port config, stream pointers, slave status, and FIFO command ids.
- `struct qcom_swrm_data` selects defaults and register layout for compatible versions.
- Register access is abstracted through CPU MMIO helpers or AHB bridge regmap helpers for SLIMbus-parented devices.
- FIFO helpers `qcom_swrm_cmd_fifo_wr_cmd()` and `qcom_swrm_cmd_fifo_rd_cmd()` implement `sdw_master_ops::xfer_msg`.
- IRQ handlers process slave alerts, enumeration/status changes, FIFO errors, bus clash, broadcast completion, clock-stop events, wake, and command-ignore events.
- `qcom_swrm_init()` resets/configures the controller, frame shape, auto-enumeration, interrupts, command retries, clock start, component enable, and FIFO depth.
- Master port ops are `qcom_swrm_port_params()`, `qcom_swrm_transport_params()`, and `qcom_swrm_port_enable()`.
- `qcom_swrm_compute_params()` maps configured Qualcomm port data into SoundWire transport and port parameters.
- ASoC DAI callbacks allocate/free master ports, hold runtime PM during stream use, and store/retrieve `sdw_stream_runtime` pointers.
- `qcom_swrm_probe()` is the platform probe and `swrm_runtime_suspend/resume()` handle PM.

## Control flow

Probe selects hardware data from OF match, chooses AHB bridge or MMIO register access, gets optional reset, IRQs, and interface clock, initializes locks/completions and bus ops, reads port configuration from hardware and device tree, initializes bus parameters/properties, requests main and optional wake IRQs, determines controller id, registers the SoundWire master, initializes the controller, waits briefly for auto-enumeration, registers DAIs, enables runtime PM, and creates debugfs if enabled.

Message transfer goes through command FIFO. Writes pack data/device/cmd-id/register into a FIFO command and optionally wait for broadcast completion. Reads enqueue a read command, wait for read FIFO data, verify command id, and retry with FIFO flush on mismatch. The IRQ handler loops over masked status bits until quiescent, updating slave status/enumeration and completing broadcast commands.

Stream setup is PDM-oriented. ASoC `.hw_params` allocates available Qualcomm master ports for the stream's slave runtime ports, then calls `sdw_stream_add_master()`. The common SoundWire stream layer calls `qcom_swrm_compute_params()` and port ops to program hardware transport registers and channel enable bits. `.hw_free` clears allocated port bits and removes the master runtime.

Runtime suspend waits for FIFO drain, optionally prepares and enters SoundWire clock stop, masks bus-clash interrupts, disables the interface clock, and enables wake IRQ. Runtime resume disables wake IRQ, enables the clock, either fully resets/reinitializes when clock stop is unsupported by an attached slave or restarts the bus and exits clock stop, then restores interrupts/status.

## State and persistence behavior

State includes `port_mask`, per-port `pconfig`, command ids, completions, `intr_mask`, cached `status[]`, `slave_status`, stream pointers, runtime PM state, FIFO depth, and `clock_stop_not_supported`. Hardware state persists in Qualcomm manager registers, command FIFOs, frame/port bank registers, interrupt masks, and clock/reset state. Port allocation is protected by `port_lock`; bus reconfiguration is handled by the generic SoundWire bus lock.

## Dependencies and integration points

The driver depends on OF/platform probing, regmap for AHB bridge mode, clk/reset APIs, PM runtime, wake IRQ support, ASoC DAI/component APIs, generic SoundWire bus/master/stream APIs, and Qualcomm DT properties such as `qcom,ports-offset1`, `qcom,ports-sinterval`, `qcom,din-ports`, and `qcom,dout-ports`.

## Risks and edge cases

- FIFO command-id mismatch handling is retry-based and can return `SDW_CMD_IGNORED`; noisy hardware can degrade bus transactions.
- `qcom_swrm_stream_alloc_ports()` calls `sdw_stream_add_master()` but does not check its return value, so allocation can appear successful when stream-add failed.
- `clock_stop_not_supported` is updated during enumeration based on slave `clk_stop_mode1`; multi-slave behavior depends on the last matching enumerated slave.
- Port configuration is DT-driven and version-sensitive; missing optional fields use `SWR_INVALID_PARAM`, but required fields fail probe.
- IRQ handler mutates `intr_mask` to disable recurring clash/collision/mismatch interrupts; recovery requires resume/init paths or manual reenable.
- Runtime resume resets/reinitializes the controller when clock stop is unsupported, which forces re-enumeration and can disturb active assumptions.
- The driver only advertises tested PDM-style DAIs despite broader SoundWire capabilities.

## Test signals

Validate all compatible layouts, MMIO and AHB bridge access, controller reset/init, auto-enumeration, FIFO read/write retries, broadcast completion, slave alert IRQs, bus clash masking, wake IRQ, runtime suspend/resume with and without clock stop, stream port allocation/free under multiple slaves, and DT port-configuration error cases. A focused test should assert `.hw_params` propagates `sdw_stream_add_master()` failures if fixed later.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/qcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/slave.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/slave.c

## Purpose

`slave.c` creates and discovers Linux SoundWire slave devices. It allocates slave objects, names/registers them on the SoundWire bus, initializes completions and locks, preloads SDCA information, supports ACPI and device-tree discovery, detects duplicate ACPI unique IDs, and exports an OF node lookup helper.

## Important APIs, types, and functions

- `sdw_slave_add()` allocates/registers a slave and adds it to `bus->slaves`.
- `sdw_slave_type` defines the slave device type, release callback, and uevent callback.
- `sdw_acpi_find_slaves()` scans ACPI children under the master and registers matching slaves.
- `sdw_of_find_slaves()` scans DT children with `compatible = "sdw..."` and matching `reg` link id.
- `of_sdw_find_device_by_node()` finds a SoundWire device by OF node.
- ACPI helpers `find_slave()`, `sdw_acpi_check_duplicate()`, and `sdw_acpi_find_one()` parse ADR, apply optional DMI ADR override, match link id, and handle unique-id suppression.

## Control flow

Discovery calls either ACPI or OF scanning. ACPI walks child devices, skips unavailable children, reads local ADR, optionally overrides it, extracts link id and slave id, performs an O(N^2) duplicate check for identical manufacturer/part/class/unique ids, optionally ignores unique id when no duplicate requires it, and calls `sdw_slave_add()`. OF scanning parses the compatible string into SoundWire version/manufacturer/part/class, reads `reg` for link and unique id, filters by bus link id, and adds the slave.

`sdw_slave_add()` initializes identity, parent/fwnode/of_node, bus/type/groups, status, completions, port-ready completions, device number, probed/interrupt flags, and a device lock. It inserts the slave into `bus->slaves` under `bus_lock`, reads SDCA interface/function data before device registration, registers the device, and initializes debugfs. Failure removes the list node and drops the device reference.

## State and persistence behavior

Each `struct sdw_slave` persists as a Linux device until release, with state for status, dev_num, sticky enumeration, completions, probed flag, first interrupt, port readiness, SDCA information, firmware node, and list membership. No hardware state is directly programmed here; enumeration and attachment status are handled by bus/controller code.

## Dependencies and integration points

This file depends on ACPI, OF, SoundWire bus type, sysfs groups from `sysfs_slave.c`, debugfs helper declarations, SDCA lookup functions, and bus helpers for ID extraction/comparison. Slave drivers bind through `sdw_bus_type` after `device_register()`.

## Risks and edge cases

- ACPI duplicate detection is O(N^2), acceptable for small numbers but sensitive to firmware errors.
- ACPI unique id may be intentionally ignored when no duplicates require it, changing device names and match behavior.
- `sdw_slave_add()` ignores the return from `sdca_lookup_*` helpers and from debugfs init.
- OF compatible parsing is strict; malformed strings are skipped.
- If `device_register()` fails, the object is freed by release after `put_device()`, so no direct free is allowed.
- The initial status group exposes status/device number before attachment; users must handle `UNATTACHED` and `N/A`.

## Test signals

Test ACPI discovery with duplicate and unique IDs, DMI ADR override, unavailable ACPI children, OF compatible/reg parsing, device-register failure, SDCA function discovery, debugfs creation, slave release of OF node and mutex, and lookup by OF node. Device names should match ignored versus explicit unique-id cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/slave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/stream.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/stream.c

## Purpose

`stream.c` is the generic SoundWire stream state machine and bus reconfiguration engine. It allocates stream/master/slave/port runtimes, validates and configures streams, computes and programs transport/port parameters, prepares/deprepares ports, enables/disables channels, performs single-link and multi-link bank switches, and exposes ASoC helper APIs for startup/shutdown.

## Important APIs, types, and functions

- Exported frame shape tables and lookup helpers: `sdw_rows`, `sdw_cols`, `sdw_find_row_index()`, `sdw_find_col_index()`.
- Public stream lifecycle APIs: `sdw_alloc_stream()`, `sdw_release_stream()`, `sdw_prepare_stream()`, `sdw_enable_stream()`, `sdw_disable_stream()`, `sdw_deprepare_stream()`, `sdw_startup_stream()`, `sdw_shutdown_stream()`.
- Runtime membership APIs: `sdw_stream_add_master()`, `sdw_stream_remove_master()`, `sdw_stream_add_slave()`, `sdw_stream_remove_slave()`.
- `sdw_get_slave_dpn_prop()` finds source/sink port capability records.
- Internal programming helpers configure slave DPn registers, master port ops, channel enable, port prepare/deprepare, bus config callbacks, SDCA clock scaling, and bank switches.
- Lock helpers acquire all involved bus locks in bus-id order and release in reverse order.

## Control flow

ASoC startup allocates a stream and installs it on all DAIs. Slave and master drivers add their runtime portions with stream configuration and port configuration; adding the first slave moves the stream to `CONFIGURED`. `sdw_prepare_stream()` locks all buses, validates state, optionally updates bus bandwidth and recomputes bus parameters, programs transport and port parameters, performs a bank switch, prepares ports on the new bank, and moves to `PREPARED`.

`sdw_enable_stream()` reprograms parameters for already prepared/disabled streams, enables slave and master channel bits in the alternate bank, bank-switches, and marks `ENABLED`. `sdw_disable_stream()` disables channel bits, marks `DISABLED`, reprograms active stream params, bank-switches, then disables the previous current bank too. `sdw_deprepare_stream()` marks `DEPREPARED`, deprepares ports, subtracts bandwidth including multi-lane accounting, recomputes/programs bus params, and bank-switches.

Bank switching writes broadcast frame control to `next_bank`. In multi-link mode, transfers are deferred with SSP sync and completed after controller `post_bank_switch()` triggers hardware sync; otherwise the bank toggles immediately. Error paths free deferred message buffers and unlock message locks.

## State and persistence behavior

Software state is spread across `sdw_stream_runtime` (`state`, params, master list, type, runtime count), `sdw_master_runtime`, `sdw_slave_runtime`, `sdw_port_runtime`, `bus->params`, bus bandwidth/lane usage, stream refcounts, and BPT refcounts. Hardware state is programmed into slave DPn/DP0 registers, master port registers via controller callbacks, bus frame control banks, and channel enable bits. The state machine allows only specific transitions and treats BPT streams as mutually exclusive with audio streams on a bus.

## Dependencies and integration points

This file depends on SoundWire register definitions, generic bus transfer APIs, controller `sdw_master_ops`/`sdw_master_port_ops`, slave driver `port_prep` and `bus_config` callbacks, SDCA clock scaling helpers, and ASoC DAI stream plumbing. Intel and Qualcomm drivers both rely on these exported APIs for PCM and BPT streams.

## Risks and edge cases

- State transitions are strict; callers that remove members or call prepare/enable out of order get `-EINVAL`.
- `_sdw_prepare_stream()` restores only one `bus->params` snapshot on error, even though it can iterate multiple buses; multi-bus error recovery should be reviewed.
- Multi-link locking combines bus locks and `msg_lock`; ordering and error unlock paths are critical.
- Port preparation polls while holding `bus_lock` because interrupts cannot be used in that context; bad timeouts can block stream setup.
- BPT streams are constrained to DP0 and mutually exclusive with audio streams by bus refcounts.
- Bandwidth accounting for multi-lane ports subtracts lane-specific bandwidth during deprepare; incorrect lane assignment can underflow counters.
- Several TODOs note missing port capability validation and asynchronous mode support.

## Test signals

Exercise all public stream transitions, invalid transition rejection, single-link and multi-link bank switch, multi-master lock ordering, BPT exclusivity, DP0 and DPn port prepare/deprepare, simple and full port types, read-only word length, SDCA clock scaling, lane-control bandwidth accounting, slave driver port callbacks, and failure injection for transfer, controller port ops, compute params, and bus_config callbacks. Lockdep and KASAN are high-value for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_local.h -->
# sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_local.h

## Purpose

`sysfs_local.h` declares local SoundWire sysfs groups and the DPn sysfs initialization helper shared by slave setup and sysfs implementation files.

## Important APIs, types, and functions

- `sdw_slave_status_attr_groups` exposes basic slave status and device number at device creation.
- `sdw_attr_groups` exposes generic SoundWire slave attributes, device properties, and DP0 attributes.
- `sdw_slave_sysfs_dpn_init()` initializes additional device-managed DPn sysfs properties after slave driver probe.

## Control flow

`slave.c` assigns `sdw_slave_status_attr_groups` to newly created slave devices. Other SoundWire driver paths use `sdw_attr_groups` and `sdw_slave_sysfs_dpn_init()` when full property exposure is appropriate after property discovery/probe.

## State and persistence behavior

The header has no state. The declared groups are static data owned by sysfs implementation files. DPn sysfs state is device-managed by the implementation.

## Dependencies and integration points

It depends on `struct sdw_slave` and is consumed by `slave.c`, `sysfs_slave.c`, and the DPn sysfs implementation in the same driver directory.

## Risks and edge cases

- The split between status-only groups and full attribute groups must match slave lifecycle; full attributes should not be exposed before properties are populated.
- Header declarations must remain synchronized with the implementation files.

## Test signals

Compile all SoundWire sysfs files together and verify slave devices expose status attributes immediately, full properties after property setup, and DPn groups after `sdw_slave_sysfs_dpn_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_slave.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_slave.c

## Purpose

`sysfs_slave.c` defines sysfs attributes for SoundWire slave devices. It exposes modalias, generic DisCo slave properties, optional DP0 properties, and basic live status/device-number attributes.

## Important APIs, types, and functions

- Macro-generated slave property attributes expose fields from `slave->prop`.
- `modalias_show()` formats the SoundWire modalias for driver matching/user inspection.
- `sdw_attr_groups` contains the modalias group, `dev-properties`, and conditional `dp0`.
- DP0 attributes expose max/min word length, supported word lengths, BRA flow control, simple channel prepare, and implementation-defined interrupts.
- `sdw_slave_status_attr_groups` contains live `status` and `device_number`.
- `dp0_attr_visible()` and `dp0_group_visible()` hide DP0 files when `slave->prop.dp0_prop` is absent.

## Control flow

When a slave device is registered, `slave.c` initially attaches status groups. After properties are available, full groups can expose the DisCo data. Reading an attribute fetches current values from `struct sdw_slave` or `slave->prop`. `device_number_show()` reports `N/A` when the slave is unattached and the numeric dev number otherwise.

## State and persistence behavior

This file owns static `attribute` and `attribute_group` definitions. It does not mutate state. Attribute values reflect current in-memory `struct sdw_slave` fields and property arrays allocated by DisCo parsing, plus live `slave->status` and `slave->dev_num` updated by enumeration.

## Dependencies and integration points

It depends on Linux sysfs/device APIs, SoundWire public types, `sdw_slave_modalias()`, and property data populated by `mipi_disco.c` and controller enumeration. `sysfs_local.h` exports the groups for use by slave setup.

## Risks and edge cases

- Several show functions assume property pointers and arrays are valid when groups are visible; exposing full groups too early can dereference null pointers.
- `device_number_show()` omits a trailing newline for both `N/A` and numeric values, which is unusual for sysfs.
- `status_show()` indexes `slave_status[]` by enum value; invalid status values would read out of bounds.
- Output uses `sprintf` into sysfs buffers; current values are small, but future list attributes should preserve bounds.

## Test signals

Validate sysfs output for unattached, attached, alert, and reserved statuses; DP0 group absence/presence; modalias format; all DisCo property fields after parsing; word list formatting; and behavior after device removal. A targeted style/regression test should check whether `device_number` should include a newline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_slave.c -->
