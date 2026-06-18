# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/StorageUnit.java`

## Purpose

`StorageUnit` is an enum that defines binary storage units from bytes through exabytes and provides conversion methods among them.

## Important APIs and Types

Enum constants are `EB`, `PB`, `TB`, `GB`, `MB`, `KB`, and `BYTES`. Each constant implements `toBytes`, `toKBs`, `toMBs`, `toGBs`, `toTBs`, `toPBs`, `toEBs`, `getLongName`, `getShortName`, `getSuffixChar`, `getDefault`, and `fromBytes`. Shared helpers `divide` and `multiply` use `BigDecimal` and scale to four decimal places.

## Control Flow

Conversions either multiply by the source unit's byte multiplier or divide by the target multiplier. `getDefault` returns the value interpreted in that enum's native unit. `toString` returns the long name. The enum declaration order intentionally puts `BYTES` last so parsing code can match longer unit suffixes before `b`.

## State and Persistence

The enum stores no mutable instance state. Static constants define binary multipliers and precision. There is no persistence beyond string names exposed by methods.

## Dependencies and Integration Points

It is used by `StorageSize.parse` and `Configuration` storage-size getters/setters. It depends on `BigDecimal` and `RoundingMode.HALF_UP` for rounded double conversions.

## Risks

Every conversion returns `double`, so large values may still lose precision even though intermediate arithmetic uses `BigDecimal`. `new BigDecimal(double)` preserves binary floating imprecision rather than decimal text intent. Four-decimal rounding can truncate meaningful precision in configuration values. Reordering enum constants can break suffix parsing.

## Test Signals

Tests should verify all pairwise unit conversions, precision/rounding behavior, very large values, negative values if allowed, `getDefault` semantics, suffix strings, and preservation of enum order assumptions used by `StorageSize`.
