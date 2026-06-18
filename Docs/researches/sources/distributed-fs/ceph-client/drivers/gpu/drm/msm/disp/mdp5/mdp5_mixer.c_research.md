# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_mixer.c

Purpose: Provides atomic allocation and release of MDP5 layer mixers (LMs), including source-split right-mixer pairing, plus construction of `struct mdp5_hw_mixer` instances from SoC config.

Important APIs/functions: `mdp5_mixer_assign()` selects a mixer for a CRTC according to required caps and current global atomic assignment state. Optional `r_mixer` requests source-split pairing, using `get_right_pair_idx()` and the hard-coded pair map LM0->LM1 and LM2->LM5. `mdp5_mixer_release()` clears a mixer-to-CRTC assignment in the duplicated global state. `mdp5_mixer_init()` fills immutable hardware metadata such as LM id, caps, ping-pong id, DSPP id, name, and CTL flush mask.

Control flow: CRTC atomic check obtains `mdp5_global_state` with locking, then asks this module to assign one or two mixers. The assign loop skips mixers owned by other CRTCs, skips mixers lacking requested caps, and prefers pair-capable mixers so later source-split transitions can avoid a full modeset when possible. Release validates that the mixer is currently assigned before clearing it.

State and persistence: Assignment is stored in `global_state->hwmixer.hwmixer_to_crtc[]`, not directly in hardware. Hardware identity is devm-allocated for device lifetime. No persistent storage exists.

Dependencies/integration: Depends on `mdp5_kms`, SoC `mdp5_lm_instance` config, DRM atomic state, CRTC objects, and CTL flush mask helpers. CRTC pipeline setup consumes the assigned mixers.

Risks and test signals: Pairing is hard-coded and assumes known MDP5 source-split combinations. Returning `-EINVAL` for missing pair capability can fail otherwise usable single-mixer modes if caller requested a right mixer. Test with multiple CRTCs, source-split wide modes, mixer release/reassign sequences, and atomic check rollback after failures.
