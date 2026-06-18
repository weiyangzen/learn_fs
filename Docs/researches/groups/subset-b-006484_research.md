<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm2200.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm2200.h

## Purpose
Private register-map header for the WM2200 ALSA SoC codec driver. It gives the C driver symbolic names for the codec's register addresses, public clock/FLL selector values, total register count, maximum register address, and detailed 16-bit field masks/shifts/widths used by regmap, ASoC controls, DAPM routes, FLL setup, digital audio interface programming, GPIO/IRQ handling, ANC/EQ/filter programming, and DSP memory/control access.

## Important APIs, Types, and Functions
This header defines no functions or types. Its API surface is macro-only:

- Clock IDs and selectors: `WM2200_CLK_SYSCLK`, `WM2200_CLKSRC_MCLK1`, `WM2200_CLKSRC_MCLK2`, `WM2200_CLKSRC_FLL`, `WM2200_CLKSRC_BCLK1`, and FLL reference selectors `WM2200_FLL_SRC_MCLK1`, `WM2200_FLL_SRC_MCLK2`, `WM2200_FLL_SRC_BCLK`.
- Register address constants from reset/revision through clocking, FLL, charge pumps, mic bias, inputs, outputs, AIF1, mixers, GPIO, interrupts, EQ, high-pass/low-pass filters, DSP1/DSP2 controls, ANC controls, and DSP1/DSP2 DM/PM/ZM windows.
- Register metadata: `WM2200_REGISTER_COUNT` is 494 and `WM2200_MAX_REGISTER` is `0x4FFF`.
- Bitfield helper macros in the pattern `*_MASK`, `*_SHIFT`, and `*_WIDTH`, plus single-bit value aliases such as `WM2200_SYSCLK_ENA`, `WM2200_FLL_ENA`, `WM2200_IN1L_ENA`, `WM2200_OUT1L_MUTE`, `WM2200_AIF1_BCLK_MSTR`, `WM2200_DSP1_START`, and `WM2200_DSP2_CORE_ENA`.

## Control Flow, State, and Persistence
There is no runtime control flow in the header. The control flow it enables is in `wm2200.c`, where the macros are consumed by regmap readability/volatility predicates, range-window setup for paged DSP memories, component controls, clock/FLL code, DAI format and TDM slot programming, DAPM power transitions, interrupt handling, and DSP firmware integration. Persistent hardware state is represented by WM2200 registers and regmap cache entries outside this header. The header's constants define which hardware locations exist, which fields are writable/status-like, and how cached 16-bit values should be masked or shifted before writes.

## Dependencies and Integration Points
The file is guarded by `_WM2200_H` and has no include dependencies of its own. It is included by `wm2200.c`, which also includes platform data from `<sound/wm2200.h>`, regmap, ASoC, regulator, GPIO, and Cirrus/Wolfson DSP support. Integration points include:

- Regmap configuration, including `wm2200_reg_defaults`, `wm2200_volatile_register()`, `wm2200_readable_register()`, and `wm2200_ranges[]` in `wm2200.c`.
- ASoC controls and DAPM widgets/routes that need stable register and field names for input/output gains, mutes, mixer sources, AIF slots, PDM speaker controls, EQ, filters, ANC, and GPIOs.
- DSP firmware loading through paged DM/PM/ZM windows and DSP control registers; the header supplies the real register windows and page-base masks used by regmap range translation.
- Board/platform policy that selects clock sources or FLL references using the exported clock selector macros.

## Risks
Because this is a generated-style hardware definition header, most risks are definition drift rather than algorithm bugs. Incorrect register addresses, max-register bounds, or duplicated generic field names could make regmap reject valid addresses, cache invalid values, or write a bit into the wrong hardware field. The repeated generic aliases such as `WM2200_IN_VU`, `WM2200_OUT_VU`, and mixer source/volume field shapes are convenient but can hide copy/paste errors if a later register differs from the repeated pattern. DSP memory and page-base definitions are especially sensitive: an off-by-one in a DM/PM/ZM limit, window length, or page-base mask can corrupt firmware load/readback across paged regions. Clock and FLL selector constants must match the hardware encoding used by `set_sysclk`/FLL programming, or audio streams can fail without an obvious compile-time signal.

## Test Signals
Useful signals are mostly build and hardware/regmap oriented: successful compilation of `wm2200.c` with all macro references resolved, regmap probe reading reset ID and revision, debugfs/regmap access accepting all expected readable addresses through `WM2200_MAX_REGISTER`, successful cache sync after reset or suspend, clock/FLL lock when selecting each supported source, AIF1 playback/capture with expected slot/word-length programming, ALSA controls correctly changing input/output gains and mutes, DAPM route tests across mixers/EQ/filters/ANC, GPIO/IRQ status/mask behavior, and DSP firmware load/readback through both DSP1 and DSP2 DM/PM/ZM windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm2200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm5100-tables.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm5100-tables.c

## Purpose
WM5100 register policy and reset-default table for the ALSA SoC codec driver. The file tells regmap which registers are volatile, which are readable, and what default 16-bit values should seed the register cache for the WM5100's clocks, FLLs, power blocks, detection blocks, audio interfaces, mixers, DSP controls, GPIOs, IRQs, EQ/DRC/filter blocks, and DSP memory controls.

## Important APIs, Types, and Functions
The file includes `wm5100.h` and exports three symbols used by the main I2C codec driver:

- `bool wm5100_volatile_register(struct device *dev, unsigned int reg)`: returns true for reset/revision, FX control, interrupt status/raw status registers, output and input status, mic-detect status, and all DSP1/DSP2/DSP3 PM/ZM/DM memory ranges.
- `bool wm5100_readable_register(struct device *dev, unsigned int reg)`: large allow-list of normal readable control/status registers plus the same DSP memory ranges. It covers software reset, revision, control interface, tone/PWM, clocking, ASRC/ISRC, FLL1/FLL2, charge pumps, LDO, mic bias/detect, inputs, outputs, three audio interfaces, mixer source/volume registers, GPIO/pad registers, IRQ registers, EQ/DRC/HPLPF blocks, and DSP1/DSP2/DSP3 controls.
- `struct reg_default wm5100_reg_defaults[WM5100_REGISTER_COUNT]`: reset/cache defaults indexed for the regmap config in `wm5100.c`.

## Control Flow, State, and Persistence
The two predicate functions are simple switch/default classifiers. Direct `case` labels handle discrete registers; the default path uses range comparisons for DSP PM/ZM/DM memory windows and returns false for anything outside the known map. No mutable driver state is held here and the unused `struct device *dev` parameter is present to match regmap callback signatures.

Persistent behavior is through the regmap cache. `wm5100.c` installs these callbacks in `wm5100_regmap` with 16-bit register and value widths, `WM5100_MAX_REGISTER`, `REGCACHE_MAPLE`, `wm5100_reg_defaults`, and `ARRAY_SIZE(wm5100_reg_defaults)`. During probe the main driver initializes I2C regmap from this table, reads/reset-identifies the chip, may register revision-A patches, and then performs normal codec setup. Registers marked volatile are not trusted from cache, while readable/defaulted registers can be cached, restored after reset, and exposed through debug paths.

## Dependencies and Integration Points
The file depends on register constants and `WM5100_REGISTER_COUNT` from `wm5100.h`, plus Linux `struct device` and regmap types made available by that header's includes. It integrates directly with:

- `wm5100_regmap` in `wm5100.c`, via `.volatile_reg = wm5100_volatile_register`, `.readable_reg = wm5100_readable_register`, and `.reg_defaults = wm5100_reg_defaults`.
- Probe/reset/revision handling in `wm5100.c`, including revision-A patch registration after `wm5100_reset()`.
- ASoC control and DAPM code in `wm5100.c`, which assumes controls refer to readable/cache-backed registers unless explicitly volatile.
- DSP handling, where PM/ZM/DM address ranges for DSP1, DSP2, and DSP3 must be readable and volatile because firmware/runtime data can change outside normal cached control writes.

## Risks
The main risk is stale or incomplete register classification. A writable control omitted from `wm5100_readable_register()` can make regmap reject reads, break cache sync, or hide a control from debug validation. A status or DSP memory location omitted from `wm5100_volatile_register()` can return stale cached values for IRQ/status paths or firmware data. Conversely, marking too much volatile reduces cache effectiveness and can increase I2C traffic. The default table is large and hand/generated data-like; wrong reset values can cause regcache sync to overwrite silicon defaults with incorrect mixer routing, clocking, GPIO, IRQ mask, EQ, DRC, or DSP control values. The defaults include many repeated mixer volume/source patterns and filter/EQ coefficients, so table-order/count drift against `WM5100_REGISTER_COUNT` or register constants is a persistent maintenance risk.

## Test Signals
Build coverage should confirm all `WM5100_*` constants still exist and that `wm5100_reg_defaults` has the expected size. Runtime signals include successful I2C regmap initialization, chip ID/revision reads, reset followed by regcache sync without unreadable-register errors, debugfs/regmap reads over all listed control and DSP ranges, IRQ/status reads reflecting live hardware changes, no stale mic/headphone/output/input status values, revision-A patch registration applying cleanly, ALSA controls modifying cached controls and surviving suspend/resume, and DSP firmware/control tests that read live PM/ZM/DM memory rather than cached values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm5100-tables.c -->
