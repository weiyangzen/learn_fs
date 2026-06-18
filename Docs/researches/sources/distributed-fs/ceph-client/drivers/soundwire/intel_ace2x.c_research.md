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
