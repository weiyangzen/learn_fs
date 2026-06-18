# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestStorageUnit.java

## Purpose

`TestStorageUnit` validates the `StorageUnit` enum's binary storage conversions, unit metadata, default behavior, and rounding expectations across bytes, KB, MB, GB, TB, PB, and EB.

## Important APIs and types

- `StorageUnit.BYTES`, `KB`, `MB`, `GB`, `TB`, `PB`, and `EB`.
- Conversion methods: `toBytes`, `fromBytes`, `toKBs`, `toMBs`, `toGBs`, `toTBs`, `toPBs`, `toEBs`, and `getDefault`.
- Metadata methods: `getShortName`, `getSuffixChar`, `getLongName`, and `toString`.

## Control flow

The first six tests provide maps of input byte counts to expected conversions for byte-to-larger-unit conversions, including negative and zero values plus values that round to four decimal places. The remaining tests validate each unit's metadata, conversion to bytes, conversion from bytes, identity conversion, and conversion to other units using binary 1024 multipliers.

## State and persistence behavior

The test is stateless. Constants define binary unit magnitudes as doubles. No configuration or filesystem state is used.

## Dependencies and integration points

The file depends on AssertJ and the `StorageUnit` enum used by `Configuration.getStorageSize`/`setStorageSize`. It anchors expected display names and suffixes consumed by config parsing.

## Risks and edge cases

- Exact double equality is used for rounded results, so implementation changes to precision or rounding policy will break tests.
- The class spells terabyte conceptually as "Terra" in method name but expects `terabytes`; naming inconsistencies can confuse future maintainers.
- Extremely large EB/PB conversions approach precision limits of `double`; the tests explicitly note out-of-precision cases.

## Test signals

The suite provides complete unit coverage for metadata and representative positive, negative, zero, small, and large conversions. Complementary tests in `TestConfiguration` cover string parsing of storage-size configuration values.
