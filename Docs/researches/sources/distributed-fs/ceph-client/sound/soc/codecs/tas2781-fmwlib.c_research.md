<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-fmwlib.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-fmwlib.c

## Purpose

This file implements firmware support for TASDEVICE/TAS2781-family amplifiers. It parses RCA binaries, DSP coefficient/program/config binaries, and calibration binaries; maps firmware block types to target amplifier channels; executes register command streams; performs optional PRAM/YRAM checksum verification; loads tuning/program/config selections; applies calibrated speaker data; and frees parsed RCA/calibration state.

## Important APIs, types, and functions

Exported APIs include `tasdevice_rca_parser()`, `tasdevice_select_cfg_blk()`, `tas2781_load_calibration()`, `tasdevice_dsp_parser()`, `tasdevice_calbin_remove()`, `tasdevice_config_info_remove()`, `tasdevice_select_tuningprm_cfg()`, `tasdevice_prmg_load()`, and `tasdevice_tuning_switch()`. Important internal helpers include `tasdevice_add_config()`, `map_dev_idx()`, the `fw_parse_*` family for kernel/git/TAS5825 layouts, `fct_param_address_parser()`, `tasdevice_process_block()`, `tasdevice_load_block_kernel()`, CRC/YRAM helpers, `tasdev_load_blk()`, `tasdevice_load_block()`, `dspfw_default_callback()`, `fw_parse_header()`, calibration conversion/preprocessing helpers, and `tasdevice_dspfw_ready()`.

## Control flow

RCA parsing validates image size, minimum version, `ndev` match, config sizes, optional profile names, and block boundaries before storing `tasdevice_config_info` arrays. DSP parsing requests the coefficient binary, validates magic/size/fixed header, selects parser/load callbacks based on driver and PPC versions, parses variable headers, program data, configuration data, and optional calibration parameter address tables. Command execution has two paths: RCA/kernel-style subblocks (`SING_W`, `BURST`, `DELAY`, `FIELD_W`) through `tasdevice_process_block()`, and legacy 4-byte command arrays through `tasdev_load_blk()`. Program/config selection marks active devices from RCA config masks, loads programs when current program differs or force load is set, then loads configurations and calibrated data for devices that successfully loaded. `tasdevice_tuning_switch()` loads pre-power-up or pre-shutdown RCA blocks around playback/tuning state.

## State and persistence behavior

The library mutates `tasdevice_priv` firmware state: `rcabin`, `fmw`, parser/load function pointers, `dspbin_typ`, current program/config, force-load state, per-device `cur_prog`, `cur_conf`, `is_loading`, `is_loaderr`, `err_code`, and calibration-specific data. Parsed firmware and calibration blocks are heap-owned until explicit remove functions free them. Calibration data can rewrite R0, inverse R0, power, and thermal limit registers, and TAS2781-specific preprocessing may adjust sine gain based on default versus calibrated impedance.

## Dependencies and integration points

The file depends on Linux firmware loading, CRC8, unaligned big-endian helpers, regmap-backed `tasdevice_dev_*` callbacks, public TAS2781 data structures/macros, and caller-populated private state such as `ndev`, `chip_id`, firmware names, CRC lookup table, and device address/channel state. It exports symbols in namespace `SND_SOC_TAS2781_FMWLIB` for higher-level TAS2781/TAS2563 drivers.

## Risks and test signals

Risks include large binary parser attack surface, many manual offset/boundary calculations, parser variants selected by firmware version, mutable per-device load state after partial failures, checksum retry semantics that can invalidate current program/config, YRAM checksum logic with excluded swap-command regions, calibration assumptions about exactly one calibration and 15 commands, and potential mismatch between RCA active-device masks and DSP program/config device counts. Test signals include malformed firmware boundary tests, valid RCA/DSP/calibration load for 1/2/4 devices, all supported drv/PPC version parser paths, single/burst/field/delay command execution, checksum pass/fail retry behavior, program/config reload avoidance, calibrated data writes including TAS2781 sine-gain adjustment, cleanup leak checks, and playback tuning switch pre-power/pre-shutdown block loading.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-fmwlib.c -->
