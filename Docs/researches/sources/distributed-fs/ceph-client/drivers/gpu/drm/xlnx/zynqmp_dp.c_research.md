# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp.c

## Purpose

`zynqmp_dp.c` implements the ZynqMP DisplayPort transmitter as a DRM bridge. It owns DP core MMIO programming, PHY/reset handling, AUX transactions, sink detection and EDID, link training, stream timing/TU programming, live-layer bus-format negotiation, debugfs test modes, HPD handling, vblank interrupt control, and minimal DP audio register helpers.

## Important APIs, Types, And Functions

Important state is `struct zynqmp_dp`, including AUX, bridge, work items, lock, PHYs, DPCD, link config, mode, test state, and flags. Public APIs are `zynqmp_dp_probe()`, `zynqmp_dp_remove()`, `zynqmp_dp_enable_vblank()`, `zynqmp_dp_disable_vblank()`, `zynqmp_dp_audio_set_channels()`, `zynqmp_dp_audio_enable()`, `zynqmp_dp_audio_disable()`, and `zynqmp_dp_audio_write_n_m()`. Major helpers include PHY init/exit/probe/ready, `zynqmp_dp_mode_configure()`, `zynqmp_dp_train_loop()`, AUX transfer, bridge atomic enable/disable/check, detect, EDID read, test-pattern debugfs, and IRQ handling.

## Control Flow

Probe allocates the bridge object, maps the `dp` resource, gets IRQ/reset/PHYs, resets hardware, initializes default RGB 8bpc config, powers down lanes, initializes PHYs, enables transmitter, requests IRQ, and exposes `dpsub->dp`/`dpsub->bridge`. Bridge attach registers AUX and enables interrupts. Detection polls HPD, reads DPCD, and records common max link rate/lane count. Atomic enable powers runtime PM, enables live DISP input if present, configures format, validates bandwidth, chooses lane/rate, programs TU and main stream timing, powers sink to D0, trains the link with downshift on failure, resets stream/AUX blocks, and enables main stream. IRQ handling clears status, reports under/overflow, handles vblank, schedules HPD/HPD-IRQ work, and completes AUX replies.

## State And Persistence Behavior

Software state persists in `struct zynqmp_dp`: connection status, enabled flag, DPCD, link capabilities, current mode, test/debugfs settings, and cached format bits. Hardware state persists in DP link, lane, PHY, AUX, main-stream, interrupt, audio, and test-pattern registers until disabled/reset. Runtime PM keeps the device active during stream/audio operations.

## Dependencies And Integration Points

It depends on DRM bridge/DP helpers, EDID/DDC through `drm_dp_aux`, OF bridge lookup, PHY framework, reset controls, common clocks through DPSUB, PM runtime, debugfs, and display-layer APIs for live input. It integrates with KMS through a bridge connector and vblank callbacks, and with audio through exported DP audio register helpers.

## Risks And Test Signals

Risks include AUX timeout tuning, HPD debounce heuristics, link training failures and downshift limits, only two lanes supported, horizontal backporch adjustment side effects, debugfs test modes overriding live link state, interrupt mask/status name confusion for reply bits, and runtime-PM balance on early errors. Test hotplug, EDID reads, modes near bandwidth limits, 1/2 lane training at RBR/HBR/HBR2, HPD IRQ retraining, vblank delivery, suspend/resume, debugfs test patterns, AUX error ignore mode, and live-input bus format negotiation.
