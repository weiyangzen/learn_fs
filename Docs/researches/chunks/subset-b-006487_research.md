# sources/distributed-fs/ceph-client/sound/soc/codecs/wm5100.h lines 4681-5311

## Scope

This chunk covers the tail of the WM5100 ALSA SoC codec private header. It is entirely declarative: register bit-field macros for DSP control and DSP memory address windows, followed by prototypes/data declarations used by the regmap-backed I2C codec driver.

The chunk starts inside the `DSP1 Control 30` field block, contains the full `DSP3 Control 30` block, enumerates representative field masks for the DSP1/DSP2/DSP3 data/program/zero memory windows, and ends the header guard after declaring the generated register-table helpers.

## Purpose

The definitions provide a source-level hardware contract for WM5100 DSP control and memory registers. The driver and its generated table code use the earlier register-address macros plus this chunk's field metadata to address the three on-chip DSP cores consistently through regmap.

The DSP memory definitions describe the externally visible register encoding for each DSP memory space:

- `DM`: data memory, 512 16-bit register words per DSP window.
- `PM`: program memory, 1536 16-bit register words per DSP window.
- `ZM`: zero/coefficient memory, 2048 16-bit register words per DSP window.

The final declarations expose the register readability/volatility predicates and default register table that `wm5100.c` installs into `struct regmap_config`.

## Important APIs, Types, and Data

- `WM5100_DSP1_*`, `WM5100_DSP2_*`, and `WM5100_DSP3_*` field macros: generated `_MASK`, `_SHIFT`, and `_WIDTH` constants for manipulating 16-bit codec registers. In this chunk, these are mostly full-width or low-byte DSP memory fields plus control bits such as `*_SYS_ENA`, `*_CORE_ENA`, and `*_START`.
- `WM5100_DSP3_RATE_MASK`, `WM5100_DSP3_DBG_CLK_ENA`, `WM5100_DSP3_SYS_ENA`, `WM5100_DSP3_CORE_ENA`, and `WM5100_DSP3_START`: bit definitions for `R4388 (0x1124) - DSP3 Control 30`. The equivalent `DSP1` definitions are completed at the top of the chunk after their `RATE`/debug fields began in the previous chunk.
- DSP memory field macros:
  - DSP1 windows: `0x4000..0x41ff` for DM, `0x4800..0x4dff` for PM, and `0x5000..0x57ff` for ZM.
  - DSP2 windows: `0x6000..0x61ff` for DM, `0x6800..0x6dff` for PM, and `0x7000..0x77ff` for ZM.
  - DSP3 windows: `0x8000..0x81ff` for DM, `0x8800..0x8dff` for PM, and `0x9000..0x97ff` for ZM.
- `bool wm5100_readable_register(struct device *dev, unsigned int reg)`: declared here and implemented in `wm5100-tables.c`; tells regmap which sparse WM5100 addresses are valid reads.
- `bool wm5100_volatile_register(struct device *dev, unsigned int reg)`: declared here and implemented in `wm5100-tables.c`; prevents regcache from treating status and DSP memory windows as stable cached registers.
- `extern struct reg_default wm5100_reg_defaults[WM5100_REGISTER_COUNT]`: exported default-value table consumed by the regmap configuration. `WM5100_REGISTER_COUNT` is 1435 and `WM5100_MAX_REGISTER` is `0x97ff`, so the default table is sparse relative to the maximum address.

## Control Flow and Integration

This header chunk has no executable control flow. Its declarations are consumed in two main places:

- `wm5100.c` defines `static const struct regmap_config wm5100_regmap` with 16-bit register and value widths, `max_register = WM5100_MAX_REGISTER`, `reg_defaults = wm5100_reg_defaults`, `volatile_reg = wm5100_volatile_register`, `readable_reg = wm5100_readable_register`, and `cache_type = REGCACHE_MAPLE`. `wm5100_i2c_probe()` passes that config to `devm_regmap_init_i2c()`.
- `wm5100-tables.c` implements the predicates declared here. Both `wm5100_volatile_register()` and `wm5100_readable_register()` treat all DSP PM/ZM/DM ranges as valid by range checks against the DSP address macros declared earlier in the header. This chunk supplies the field semantics for the same address ranges and closes the interface that makes those helpers available to the main driver.

Runtime register access flows through ALSA SoC component helpers and regmap. Higher-level paths in `wm5100.c` configure clocks, FLLs, DAPM routes, mixers, volume controls, and jack detection by writing named registers from this header. For the DSP ranges in this chunk, regmap validation and cache policy matter even when there is no direct field-manipulating code in this chunk.

## State and Persistence Behavior

The macros are compile-time constants and do not persist state. Runtime persistence is delegated to regmap:

- Nonvolatile registers can be cached using `REGCACHE_MAPLE`, with reset defaults seeded from `wm5100_reg_defaults`.
- Volatile registers, including all DSP PM/ZM/DM windows, are read from hardware rather than trusted from cache.
- DSP memory windows are stateful hardware memory. Writes to those registers can represent firmware, coefficients, or runtime DSP data and should not be considered stable across reset, suspend, or DSP core restart unless higher-level DSP management reloads them.
- The control bits in `DSPx Control 30` gate DSP clock/debug/core/system/start state. Their ordering and persistence are hardware-defined; this chunk only provides the bit locations.

## Dependencies

- Kernel headers: `<sound/soc.h>` for ALSA SoC types and `<linux/regmap.h>` for `struct reg_default`.
- `struct device` and `bool` are provided through included kernel headers.
- The main codec implementation depends on these declarations linking with `wm5100-tables.c`; otherwise `wm5100.c` cannot initialize its regmap configuration.
- The generated tables depend on the address macros immediately above this chunk, especially `WM5100_DSP[123]_{DM,PM,ZM}_{0,end}` and `WM5100_DSP[123]_CONTROL_30`, to classify readable/volatile registers.
- Hardware integration depends on the I2C regmap using 16-bit register addresses and 16-bit values; the DSP PM/DM/ZM fields are expressed as 8-bit or 16-bit portions of that register protocol.

## Risks and Edge Cases

- The header is generated-style register metadata. A changed mask, shift, or width can silently redirect bit operations to the wrong hardware field.
- The chunk begins mid-register-block for `DSP1 Control 30`; merge/reconciliation should keep the previous chunk associated with this one so the complete DSP1 control semantics are not lost.
- DSP memory spaces are very large and sparse compared with ordinary control registers. Off-by-one range constants around `0x41ff`, `0x4dff`, `0x57ff`, `0x61ff`, `0x6dff`, `0x77ff`, `0x81ff`, `0x8dff`, and `0x97ff` would affect regmap readability/volatility decisions for entire windows.
- All DSP PM/ZM/DM windows are marked volatile in `wm5100-tables.c`. Treating them as cacheable would risk stale firmware/data reads and incorrect suspend/resume behavior.
- The field macros expose both byte-sized low portions (`*_START_1`, `*_END_1`, `*_1_1`, `*_1_2`) and full 16-bit portions for multi-register memory encodings. Callers must respect the hardware packing instead of assuming every logical DSP word maps to one named full-width macro.
- `wm5100_reg_defaults` is declared with a fixed count. If register address definitions or generated defaults diverge, regmap initialization can misrepresent reset state or reject valid accesses.

## Test Signals

Useful validation signals for this chunk are mostly build, regmap, and hardware smoke tests:

- Build the WM5100 codec objects and confirm `wm5100.c` links against `wm5100_readable_register`, `wm5100_volatile_register`, and `wm5100_reg_defaults`.
- Compile with warnings enabled to catch missing prototypes, duplicate macro names, or mismatched `WM5100_REGISTER_COUNT` declarations.
- Exercise `wm5100_i2c_probe()` on WM5100 hardware or an emulated regmap path and confirm `devm_regmap_init_i2c()` accepts the sparse register map through `WM5100_MAX_REGISTER`.
- Verify readable/volatile predicate behavior for representative boundary registers: first and last PM/ZM/DM locations for each DSP core, plus one address just outside each range.
- Validate DSP bring-up or firmware-load scenarios by writing/reading known DSP memory locations and toggling `DSPx Control 30` start/core/system bits through regmap.
- Run ALSA codec smoke tests that cover probe, reset, suspend/resume, DAPM power transitions, and any DSP-enabled audio route if the platform exposes the DSP cores.
