# sources/distributed-fs/ceph-client/include/linux/regmap.h

## Purpose

`regmap.h` declares the generic register-map framework used by device drivers to access hardware registers through a common abstraction across I2C, SPI, MMIO, SPMI, SoundWire, MDIO, FSI, and other buses. It also exposes register caching, range translation, field access, polling helpers, and generic regmap-backed IRQ chips.

## Important APIs, Types, and Functions

Core data definitions include `enum regcache_type`, `struct reg_default`, `struct reg_sequence`, `struct regmap_range`, `struct regmap_access_table`, `struct regmap_config`, `struct regmap_range_cfg`, `struct regmap_sdw_mbq_cfg`, and `struct regmap_bus`. `regmap_config` is the central device-side contract: register/value bit widths, stride/shift/base, access callbacks/tables, default values, cache type, endian policy, raw I/O limits, locking policy, hardware spinlock configuration, no-increment access, single/bulk/multi-write behavior, and paged ranges.

Initialization macros wrap lockdep-keyed internal functions: `regmap_init*()` and `devm_regmap_init*()` variants exist for generic bus contexts plus I2C, MDIO, SCCB, SlimBus, SPI, SPMI base/ext, 1-Wire, MMIO with optional clock, AC97, SoundWire, SoundWire MBQ, I3C, SPI AVMM, and FSI. Runtime access APIs include `regmap_read()`, `regmap_write()`, raw/bulk/noinc/multi read-write, async writes, `regmap_update_bits_base()`, inline `regmap_update_bits*()`, `regmap_set_bits()`, `regmap_clear_bits()`, `regmap_assign_bits()`, `regmap_test_bits()`, and polling macros.

Cache APIs include `regcache_sync()`, `regcache_sync_region()`, `regcache_drop_region()`, `regcache_cache_only()`, `regcache_cache_bypass()`, `regcache_mark_dirty()`, and `regcache_reg_cached()`. Field APIs include `struct reg_field`, `REG_FIELD`, `REG_FIELD_ID`, allocation/free/devm/bulk helpers, and `regmap_field_*()`/`regmap_fields_*()` operations. IRQ support is described by `struct regmap_irq_type`, `struct regmap_irq`, `struct regmap_irq_chip`, registration/deletion APIs, and virtual IRQ/domain lookup helpers.

## Control Flow

A driver defines a `regmap_config`, initializes a map through the appropriate bus/devm macro, then performs register operations through the generic API. The framework formats register addresses and values, applies masks and endian conversions, checks readable/writeable/volatile/precious/noinc ranges, serializes access using mutex/spinlock/custom/hwspinlock policy, consults or updates cache state, and calls bus-specific operations.

`regmap_update_bits*()` performs read-modify-write unless a custom bus `reg_update_bits` path exists. Polling macros repeatedly call `regmap_read()` or `regmap_field_read()` until the caller's condition or timeout. Range configs implement indirect/paged register access by updating a selector register before using a window. IRQ chips read status registers, apply mask/unmask/ack/wake/type config policy, and map regmap IRQ descriptors into Linux IRQ domains.

When `CONFIG_REGMAP` is disabled, most APIs become warning stubs returning `-EINVAL`, `NULL`, or safe default values, allowing generic code to build while detecting invalid runtime use.

## State and Persistence Behavior

Runtime state lives in opaque `struct regmap`: bus context, device pointer, lock state, cache, async queue, range/page state, clock attachment, and optional IRQ chip data. Cache state can intentionally diverge from hardware during cache-only or bypass modes and must be synchronized explicitly. Register writes may persist in hardware across driver lifetime, suspend, or reset depending on the device.

## Dependencies and Integration Points

The header depends on device model types, lockdep, lists, rbtrees, fwnode, delays, polling, and bus-specific forward declarations. It is a major integration point for MFD, regulator, clock, GPIO, audio, PMIC, networking PHY, SoundWire, and interrupt-controller drivers. Regulator helpers in `regulator/driver.h` frequently use regmap-backed selector, enable, bypass, discharge, ramp, and current-limit operations.

## Risks

Incorrect register bit widths, endian settings, stride/shift/base, cache defaults, or volatile/precious markings can corrupt hardware state or return stale values. Relaxed MMIO requires explicit barriers when ordering matters. Disabling locking is only safe with external serialization. Cache-only and bypass modes can lose writes if dirty/sync handling is wrong. Clear-on-read status registers must be marked precious or handled carefully. Regmap IRQ inversion and mask/unmask polarity fields are easy to misconfigure.

## Test Signals

Tests should cover bus-specific init, lockdep keys, raw/bulk/noinc limits, endian formatting, range access, cache sync/drop/bypass/cache-only behavior, update-bits change reporting, async completion, polling timeouts, field allocation and per-id fields, disabled-`CONFIG_REGMAP` build stubs, and regmap IRQ masking/acking/type/wake behavior using mock devices or regmap KUnit tests.
