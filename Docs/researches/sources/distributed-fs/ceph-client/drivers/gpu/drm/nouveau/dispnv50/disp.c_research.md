<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.c

### Purpose
`disp.c` is the central NV50+ Nouveau KMS display implementation. It creates EVO/NVD channels, DRM connectors/encoders/CRTCs, audio and HDMI infoframe plumbing, DisplayPort MST management, output-resource programming, atomic state allocation/check/commit, suspend/resume hooks, and display format-modifier lists.

### Key APIs And Functions
Channel helpers include `nv50_chan_create()`, `nv50_dmac_create()`, `nv50_dmac_wait()`, and `nv50_dmac_kick()`. Output helpers include `nv50_dac_create()`, `nv50_sor_create()`, `nv50_pior_create()`, `nv50_outp_atomic_check()`, `nv50_real_outp()`, HDMI/audio helpers, and MST structures/functions (`nv50_mstm`, `nv50_mstc`, `nv50_msto`). Atomic entry points are `nv50_disp_atomic_check()`, `nv50_disp_atomic_commit()`, and `nv50_disp_atomic_commit_tail()`. Lifecycle entry points are `nv50_display_create()`, `nv50_display_init()`, `nv50_display_fini()`, and `nv50_display_destroy()`.

### Control Flow And State
Creation allocates `nv50_disp`, a shared VRAM sync BO, the core channel, capability object, format modifiers, encoder/connector objects from NVIF output info, heads from the display head mask, optional MST encoders, and audio component registration. Atomic check builds output-change records, handles static window mapping, asks DRM helpers and MST helpers to validate state, and resolves CRC conflicts. Atomic commit prepares planes, swaps state, sequences output/head/window disable and enable operations under `disp->mutex` when needed, performs core/window interlocked updates, handles MST payload part1/part2, waits for plane notifiers, sends vblank events, and coordinates CRC notifier contexts.

### Dependencies And Integration
The file depends on DRM atomic, connector, EDID, HDMI, DP, MST, vblank, framebuffer, runtime-PM, component/audio, and Nouveau NVIF output/channel/memory APIs. It integrates every local dispnv50 subsystem: `core`, `head`, `wndw`, `base`, `ovly`, `curs`, `crc`, and output-resource function tables.

### Risks And Test Signals
This file is timing-sensitive and stateful. Risks include push-buffer wrap and VRAM coherency, runtime-PM reference imbalance, MST payload ordering, audio ELD races, CRC/output reprogramming conflicts, initial state readback mismatches, and generation-specific format modifier selection. Tests should cover blocking and nonblocking atomic commits, DP/HDMI/LVDS/DAC/PIOR outputs, MST hotplug and payload changes, suspend/resume, vblank events, plane notifier timeouts, audio ELD notification, and Pascal VRAM push-buffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.c -->
