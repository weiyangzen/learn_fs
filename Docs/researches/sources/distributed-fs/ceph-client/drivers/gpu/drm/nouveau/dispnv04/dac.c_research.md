# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/dac.c

## Purpose
`dac.c` implements analog DAC encoder support for legacy Nouveau display hardware, including output offset calculation, load detection, DPMS clock gating, mode setup, save/restore, and encoder creation.

## Important APIs, Types, And Functions
`nv04_dac_output_offset()` maps DCB output routing bits to RAMDAC register offsets. `nv04_dac_detect()` performs NV04-style VGA load detection by manipulating VGA sequencer/CRTC/RAMDAC palette state and sampling during hblank. `nv17_dac_sample_load()` performs newer sample-load detection with PBUS power controls, GPIO TVDAC state, testpoint data, and RAMDAC sense bits; `nv17_dac_detect()` interprets it. Mode helpers include `nv04_dac_mode_fixup`, `nv04_dac_prepare`, `nv04_dac_mode_set`, `nv04_dac_commit`, `nv04_dac_dpms`, save/restore/destroy, `nv04_dac_update_dacclk()`, `nv04_dac_in_use()`, and `nv04_dac_create()`.

## Control Flow, State, And Integration
Encoder creation allocates `nouveau_encoder`, selects NV04 or NV17 helper funcs based on display architecture, initializes a DRM DAC encoder, sets possible CRTCs from DCB heads, and attaches it to the connector. Prepare powers the encoder down and disables any DFP remnants on the target head. Mode set binds DAC clocks to the selected CRTC and programs RAMDAC test control. DPMS tracks `last_dpms` and updates a per-output `dac_users` bitmask so shared DAC clocks are only disabled when no encoder uses them.

## State, Dependencies, Risks, And Tests
State includes DCB output routing, `dac_users`, saved RAMDAC output registers, VGA palette/CRTC/SEQ state during detection, PBUS power-control state, and optional GPIO TVDAC state. Dependencies include low-level Nouveau register helpers, NVIF MMIO access, GPIO subdev, and DCB connector metadata. Risks include flicker during load detection, incomplete head-A-only NV04 detection, fragile save/restore around palette and power controls, shared-DAC conflicts, and chipset-specific test values. Test signals are VGA hotplug/load detection, analog modeset, DPMS cycling, dual-head DAC sharing, TV DAC detection, and restore after suspend/VT switch.
