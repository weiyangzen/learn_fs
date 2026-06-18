# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-afdo.c

## Purpose
`coresight-cfg-afdo.c` provides preloaded CoreSight system-configuration descriptors for ETMv4 AutoFDO-style periodic trace capture. When ETMv4 source support is enabled, it defines a reusable `strobing` feature and an `autofdo` configuration that applies that feature with a set of preset mark/space ratios.

## Important APIs, Types, And Functions
The file declares `strobe_params` with `window` and `period` defaults. `strobe_regs` describes ETMv4 resource selector, sequencer, counter, reload, and view-inst register programming using `struct cscfg_regval_desc`. Some entries are resources, some save volatile counter values on disable, and reload registers use `CS_CFG_REG_TYPE_VAL_PARAM` to bind values to feature parameters.

`struct cscfg_feature_desc strobe_etm4x` is the feature export. `struct cscfg_config_desc afdo_etm4x` is the configuration export; it references `strobing`, declares nine presets, and supplies `afdo_presets`.

## Control Flow
There is no executable control flow beyond static descriptor construction. The CoreSight syscfg preload path imports these descriptors through `coresight-cfg-preload.c`, after which the generic configuration loader validates feature references, matches features to ETMv4 devices, and programs them through per-device config support.

## State And Persistence
The descriptors are static module data. Runtime state is created elsewhere when these descriptors are loaded into `cscfg_feature_csdev` and `cscfg_config_csdev` instances. The preset matrix is immutable and indexed by the generic config code when a perf/user configuration chooses a preset.

## Dependencies And Integration Points
This file depends on `coresight-config.h` for descriptor types and on ETMv4 config register definitions from `coresight-etm4x-cfg.h`. It is compiled only when `CONFIG_CORESIGHT_SOURCE_ETM4X` is available and is exposed through `coresight-cfg-preload.h`.

## Risks
Descriptor correctness is critical: wrong ETMv4 offsets, resource IDs, masks, or parameter indexes will program trace sources incorrectly. The `afdo_presets` comments describe varying period while holding window constant, but the second parameter values are small multipliers/period settings; tests should confirm generic code interprets them exactly as intended for ETMv4 counter reload values.

## Test Signals
Expected tests include descriptor load success, configfs/syscfg visibility of `strobing` and `autofdo`, ETMv4 feature matching, each preset index programming the counter reload registers, and trace captures showing periodic windows. Negative tests should verify builds without ETMv4 exclude these exports.
