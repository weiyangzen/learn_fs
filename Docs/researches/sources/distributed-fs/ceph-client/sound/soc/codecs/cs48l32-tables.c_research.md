# sources/distributed-fs/ceph-client/sound/soc/codecs/cs48l32-tables.c

## Purpose

`cs48l32-tables.c` supplies the CS48L32 regmap data and revision patch helper used by the main CS48L32 SPI codec driver. It defines a small Rev A patch, the default register cache image, the readable/volatile/precious register policies, the 32-bit big-endian SPI regmap configuration, and the exported helper that creates the regmap.

## Important APIs, Types, and Functions

- `cs48l32_reva_patch[]` is a `struct reg_sequence` array applied by `regmap_register_patch()`.
- `cs48l32_apply_patch()` registers the patch against `cs48l32->regmap` and reports failures with `dev_err_probe()`.
- `cs48l32_reg_default[]` is the regcache default table. It covers GPIO defaults, clocks, sample rates, FLL, charge pump/LDO/MICBIAS, IRQ masks, input controls, ASP controls, mixer source defaults, ISRC/EQ/DRC/LHPF/TONE/NOISE/ultrasonic controls, and selected DSP/IRQ masks.
- `cs48l32_readable_register()` explicitly allows register ranges including identity/reset/control, clocks, FLL, power, inputs, ASPs, mixers, EQ/DRC/LHPF, ultrasonic blocks, IRQ status/mask registers, and DSP memory/register windows.
- `cs48l32_volatile_register()` marks identity/status/reset, live clock/FLL/input status, IRQ status/event registers, and DSP memory/control windows volatile so regcache does not trust stale values.
- `cs48l32_precious_register()` marks packed DSP memory windows precious to keep regmap debugfs from issuing illegal unaligned accesses.
- `cs48l32_create_regmap()` calls `devm_regmap_init_spi()` with `cs48l32_regmap` and stores the result in `cs48l32->regmap`.

## Control Flow

The main driver calls `cs48l32_create_regmap()` early in SPI probe, then places the regmap in cache-only mode until power and reset sequencing are complete. After boot, the main probe path calls `cs48l32_apply_patch()` to apply the revision-specific register writes. Runtime suspend/resume in the main driver relies on the regcache defaults and volatile/readable policies defined here to decide what can be cached and what must be re-read or synchronized after power transitions.

## State and Persistence Behavior

This file does not allocate long-lived objects directly, but it defines the persistent regcache baseline. The `REGCACHE_MAPLE` cache stores writable, nonvolatile register state while the device is runtime-suspended or powered down. Volatile and precious markings prevent unsafe or stale cached access to status and DSP memory windows. The regmap is 32-bit register, 32-bit value, 4-byte stride, 32 pad bits, and big-endian for both register and value formatting, matching the CS48L32 SPI bus protocol.

## Dependencies and Integration Points

- Includes public CS48L32 structures from `<sound/cs48l32.h>` and register constants from `<sound/cs48l32_registers.h>`.
- Includes the local private header `cs48l32.h` for `struct cs48l32` and prototypes.
- Integrates with Linux regmap and regulator/device infrastructure.
- The main `cs48l32.c` file depends on `cs48l32_apply_patch()` and `cs48l32_create_regmap()`.

## Risks and Edge Cases

- Register policy omissions are high impact: a missing readable register can make legitimate driver access fail; a missing volatile marking can cache live status; an incorrect precious marking can expose unsafe debugfs access to packed DSP memory.
- The patch is named Rev A in code but is applied unconditionally by the main driver after ID/revision reads. If later revisions need different patches, the dispatch logic is not present here.
- The default table must stay synchronized with hardware reset values and with writes performed by probe/runtime resume. Wrong defaults can cause regcache sync to restore stale or invalid state after suspend.
- The packed DSP memory comment documents a bus-bridge alignment constraint; accidental debug or regmap bulk access outside aligned block rules can cause illegal bus transactions.

## Test Signals

Validation should cover SPI regmap creation, patch application, successful regcache sync after runtime resume, debugfs/register-dump behavior avoiding precious DSP memory, and normal driver accesses to all registers used by `cs48l32.c`. Build tests should catch prototype drift with `cs48l32.h` and register-name drift with generated/public CS48L32 register headers.
