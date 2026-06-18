# sources/distributed-fs/ceph-client/sound/soc/codecs/tfa989x.c

## Purpose

`tfa989x.c` supports NXP/Goodix TFA9890/TFA9895/TFA9897 smart speaker amplifiers in a simplified DSP-bypass mode. It verifies the hardware revision, applies revision-specific initialization, disables the undocumented CoolFlux DSP path, and registers a playback DAI with DAPM speaker/receiver routing.

## Important APIs, Types, and Functions

`struct tfa989x_rev` maps an expected revision ID to an init function. `struct tfa989x` stores revision data, the `vddd` regulator, and optional TFA9897 receiver-mode GPIO. Revision setup is split across `tfa9890_init()`, `tfa9895_init()`, and `tfa9897_init()`. `tfa989x_dsp_bypass()` programs the common bypass path. `tfa989x_hw_params()` maps rates with `tfa989x_find_sample_rate()`. `tfa989x_put_mode()` combines a TFA9897 ALSA enum write with GPIO receiver-mode control.

## Control Flow

I2C probe gets OF match data, enables the `vddd` regulator, creates a regmap, does a dummy revision read, verifies the revision ID, resets I2C registers, runs the revision init hook, enables DSP bypass, disables regcache bypass, and registers the component/DAI. DAPM powers `POWER`, then `AMPE`, then `OUT`. For TFA9897 only, component probe adds a `Mode` enum that selects speaker or receiver.

## State and Persistence Behavior

Hardware-visible state is written during probe while regcache bypass is active, then normal cached regmap operation resumes. The regulator is disabled by a managed cleanup action. There is no firmware profile persistence; the driver deliberately avoids proprietary DSP containers and accepts the reduced feature set.

## Dependencies and Integration Points

Dependencies are I2C, regmap, regulators, optional GPIO descriptors, and ASoC. Integration is OF-only via `nxp,tfa9890`, `nxp,tfa9895`, or `nxp,tfa9897`, with a `vddd` supply and optional `rcv` GPIO for TFA9897.

## Risks and Edge Cases

The driver bypasses the DSP, so speaker protection/optimization and volume profiles may be absent. Revision mismatch aborts probe, which is safer but sensitive to match data errors. Only S16_LE playback from 8 kHz to 48 kHz is exposed. Initialization writes include undocumented/hidden registers, so datasheet drift or incompatible silicon variants are risky.

## Test Signals

Validate revision detection on all compatible strings, regulator cleanup on failed probe paths, sample-rate programming, DAPM power-up to audible output, optional receiver GPIO behavior on TFA9897, and absence of I2C errors during hidden-register init sequences.
