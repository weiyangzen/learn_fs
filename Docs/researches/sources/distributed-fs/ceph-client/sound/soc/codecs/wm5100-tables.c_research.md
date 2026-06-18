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
