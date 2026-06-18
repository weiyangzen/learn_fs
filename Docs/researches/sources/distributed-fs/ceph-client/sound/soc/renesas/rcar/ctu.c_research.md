# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ctu.c

## Purpose

`ctu.c` implements the Channel Count Conversion Unit. It exposes ALSA controls for pass-through channel routing and four matrix rows of scale values, applies those controls to CTU registers, and attaches the matching CMD block so CTU can participate in SCU processing chains.

## Important APIs, types, and functions

`struct rsnd_ctu` stores the embedded module, mixer-control configs for `CTU Pass`, `CTU SV0` through `CTU SV3`, a reset control, a channel cache, and flags. `rsnd_ctu_probe()` allocates one module per DT child, deriving hardware CTU ID as `id / 4` and sub-ID as `id % 4`. `rsnd_ctu_probe_()` attaches CMD by raw module ID. `rsnd_ctu_init()` powers the module, resets/activates it, and calls `rsnd_ctu_value_init()`. `rsnd_ctu_pcm_new()` registers the ALSA controls once per CTU module. `rsnd_ctu_value_reset()` clears software control values when the reset control is set.

## Control Flow

During probe each CTU child gets a clock named by CTU group (`ctu.0`, `ctu.1`, etc.) and an `rsnd_mod` with custom ID callbacks. During PCM creation the control set is installed. At stream init, CTU powers on, pulses `CTU_SWRSR`, initializes the CTU operation, writes channel count, pass routing (`CTU_CPMDR`), matrix row count (`CTU_SCMDR`), and selected scale registers, then cancels initialization. Quit halts the block and powers it off.

## State and Persistence Behavior

Control values live in `rsnd_kctrl_cfg_m/s` fields and persist across stream starts until explicitly changed or reset. Hardware register state is rebuilt at each init. `KCTRL_INITIALIZED` prevents duplicate ALSA control registration, important because shared or mixed paths may call `pcm_new` repeatedly.

## Dependencies and Integration Points

CTU depends on common control registration from `core.c`, pseudo-register access from `gen.c`, CMD attachment from `cmd.c`, and DT connection parsing through `rsnd_parse_connect_ctu()`. It feeds MIX/DVC or CMD paths and uses common module lifecycle sequencing.

## Risks and Test Signals

Risks include raw-vs-group CTU ID confusion, duplicated controls across mixed paths, invalid pass/matrix combinations, and CTU plus TDM split misuse noted by `core.c`. Tests should cover control creation, amixer-driven matrix changes before and during stream setup, reset behavior, CTU00-CTU13 ID mapping, and audio validation for channel swap/upmix/downmix cases.
