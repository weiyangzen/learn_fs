# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-clsh-v2.c

## Purpose

`wcd-clsh-v2.c` implements the exported Class-H/Class-AB supply and headphone mode controller shared by WCD93xx-family codecs. It owns a small `struct wcd_clsh_ctrl` state object and translates logical Class-H events from codec DAPM paths into register writes for buck, flyback, Class-H CRC/DSM routing, gain path selection, and headphone PA bias modes. The source was read as a complete 902-line file.

## Important APIs, Types, and Functions

`struct wcd_clsh_ctrl` stores the current Class-H state and mode, reference counts for `flyback_users`, `buck_users`, and `clsh_users`, the codec version selector, and the owning `snd_soc_component`.

Exported entry points are `wcd_clsh_ctrl_alloc()`, `wcd_clsh_ctrl_free()`, `wcd_clsh_ctrl_set_state()`, `wcd_clsh_ctrl_get_state()`, and `wcd_clsh_set_hph_mode()`. Internal helpers split into v2/WCD9335-style and v3/WCD937x+ style paths: `wcd_clsh_state_ear()`, `wcd_clsh_state_hph_l()`, `wcd_clsh_state_hph_r()`, `wcd_clsh_state_lo()`, `wcd_clsh_v3_state_ear()`, `wcd_clsh_v3_state_hph_l()`, `wcd_clsh_v3_state_hph_r()`, and `wcd_clsh_v3_state_aux()`. Lower-level helpers program buck/flyback enables and modes, Class-H K coefficients, headphone power levels, IQ forcing, and gain path selection.

## Control Flow

Codec drivers call `wcd_clsh_ctrl_set_state()` on `WCD_CLSH_EVENT_PRE_DAC` to enable the requested path and on `WCD_CLSH_EVENT_POST_PA` to disable it. The public function validates that `nstate` is one of the defined singleton states, dispatches to `_wcd_clsh_ctrl_set_state()`, and records `ctrl->state` and `ctrl->mode`.

The state dispatcher selects an output path by requested state, then selects v2 or v3 programming based on `codec_version >= WCD937X`. Enable flows generally configure regulator mode, set buck/flyback mode, enable flyback, set flyback current, enable buck, and program headphone/line/ear path state. Disable flows reverse the PA/headphone mode, disable per-path Class-H routing where relevant, decrement buck/flyback/Class-H reference counts, and restore normal/default modes. Hardware-mandated `usleep_range()` delays are embedded after supply transitions.

## State and Persistence Behavior

All persistent state is in `struct wcd_clsh_ctrl`; there is no file-backed persistence. `buck_users`, `flyback_users`, and `clsh_users` protect shared hardware resources across left/right headphone, ear, lineout, and aux users. The code clamps `clsh_users` back to zero if it underflows, but buck/flyback counters are not similarly clamped. Hardware state persists in codec registers until later DAPM events or driver teardown write new values.

## Dependencies and Integration Points

The implementation depends on ASoC `snd_soc_component_*` register access, delay helpers, `wcd9335.h` register definitions, and `wcd-clsh-v2.h` public enums. It is integrated by `wcd9335.c` headphone, ear, and lineout DAC DAPM events, and is designed to support newer codec register layouts through version checks.

## Risks and Edge Cases

`wcd_clsh_ctrl_set_state()` accepts only singleton bit values even though state macros are bitmasks; callers that try to pass combined HPHL|HPHR state will be rejected. Several internal state functions log invalid mode combinations but return through the public API as success because `_wcd_clsh_ctrl_set_state()` always returns zero. Supply reference counters rely on balanced PRE_DAC/POST_PA calls; unbalanced disable paths can underflow buck/flyback counters and potentially desynchronize hardware enables. v2 K1 values are hard-coded for an assumed 16-ohm headphone impedance. The controller has no internal locking, so caller-side serialization through DAPM/component sequencing is assumed.

## Test Signals

Useful signals are kernel build coverage for `CONFIG_SND_SOC_WCD9335`, DAPM playback path tests for EAR/HPHL/HPHR/lineout, register trace checks around PRE_DAC and POST_PA ordering, balanced reference count tests for concurrent HPHL/HPHR enablement, and audio validation for click/pop behavior around the documented 100 us, 500 us, 1 ms, 5 ms, and 7 ms waits.
