# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_audmix.c

## Purpose
`fsl_audmix.c` is the NXP AUDMIX ASoC DAI driver. It exposes two playback TDM inputs and one capture mixed output, provides mixer/attenuation ALSA controls, enforces safe output-source and mix-clock state transitions based on started TDM streams, configures DSP_A DAI format polarity, tracks active TDM playback DAIs, manages regmap/cache/runtime PM, and optionally spawns an `imx-audmix` card device for legacy-style DTs.

## Important APIs, Types, and Functions
- Enum tables define user controls for TDM selection, output source mode, output width, enable/disable, attenuation direction, and error masks.
- `struct fsl_audmix_state` and the `prms[4][4]` matrix encode allowed state transitions and required active TDMs/clock changes.
- `fsl_audmix_state_trans()` checks active TDM requirements and prepares control-register updates.
- `fsl_audmix_put_mix_clk_src()` validates that both the current and requested clock sources are backed by started TDMs before changing clock source.
- `fsl_audmix_put_out_src()` validates output-source transitions and updates `FSL_AUDMIX_CTR`.
- `fsl_audmix_snd_controls[]` exposes mixer routing, output width, error masks, sync mode, and per-TDM attenuation controls.
- `fsl_audmix_dai_set_fmt()` accepts DSP_A plus provider/consumer combinations and maps clock inversion to output clock polarity.
- `fsl_audmix_dai_trigger()` tracks active playback TDM DAIs in `priv->tdms`.
- The DAI array exposes `audmix-0`, `audmix-1` playback inputs and `audmix-2` capture output, all fixed at 8 channels.

## Control Flow
Probe maps AUDMIX registers, creates a flat regmap with defaults, obtains the `ipg` clock, initializes the lock, enables runtime PM, and registers the component with three DAIs. If the DT node has a `dais` property, it also registers an `imx-audmix` platform device; otherwise an audio graph card is expected to connect the DAIs.

At runtime, playback trigger start sets the bit for the DAI ID in `priv->tdms`; stop clears it. Capture triggers are ignored because the active-source constraints are tied to playback inputs. Userspace control writes for output source and clock source read the current control register, check active TDM bits, optionally adjust mix clock, and then update the hardware register. DAI format configuration validates DSP_A and clock-provider flags and writes output clock polarity.

Runtime resume enables `ipg_clk`, switches regmap out of cache-only mode, marks cache dirty, and syncs registers. Runtime suspend switches regmap cache-only and disables the clock. System sleep uses runtime PM force helpers.

## State and Persistence
`priv->tdms` is the key runtime state tracking which playback TDMs are active; it is protected by `priv->lock` in trigger paths but read by control paths without taking that lock. Register state persists through regmap cache during runtime suspend. Optional child platform device state persists until remove.

## Dependencies and Integration Points
The driver depends on ASoC component/DAI/control APIs, regmap MMIO, runtime PM, `ipg` clock, DT compatibles `fsl,imx8qm-audmix` and `fsl,imx952-audmix`, and either audio graph card wiring or the spawned `imx-audmix` card driver. ALSA controls are the primary userspace integration surface for mixer routing and attenuation.

## Risks and Edge Cases
- Control callbacks read `priv->tdms` locklessly while triggers update it under spinlock, creating a small race in concurrent control/trigger operations.
- Transition constraints rely on the hard-coded `prms` matrix; new modes or semantics require careful matrix updates.
- DAI IDs are used as bit positions; adding/reordering DAIs can break `tdms` semantics.
- The driver accepts both `BC_FC` and `BP_FP` clock-provider cases but rejects other valid-looking combinations; graph card format settings must match.
- Optional child platform registration must be removed exactly once; current remove handles `priv->pdev`.

## Test Signals
- ALSA control changes for output source and clock source should fail when required TDM streams are not running and succeed when they are.
- Start/stop both playback TDMs and capture mixed output while toggling controls to validate transition matrix behavior.
- Runtime suspend/resume should preserve control settings through regcache.
- DTs with and without `dais` property validate both child-card and audio-graph integration modes.
