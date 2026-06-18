# sources/distributed-fs/ceph-client/fs/ext4/inode-test.c

## Purpose
`inode-test.c` is a KUnit suite for ext4 inode timestamp decoding. It verifies that `ext4_decode_extra_time()` correctly reconstructs `struct timespec64` seconds and nanoseconds from the legacy 32-bit inode timestamp field plus the ext4 extra timestamp bits. The tested cases are derived from the timestamp range table in `Documentation/filesystems/ext4/inodes.rst`.

The file is intentionally small and self-contained. It does not construct a filesystem, mount ext4, or mutate persistent state; it focuses on the pure decoding contract that inode load paths in `inode.c` use through macros such as `EXT4_INODE_GET_CTIME()`, `EXT4_INODE_GET_ATIME()`, and `EXT4_INODE_GET_MTIME()`.

## Important APIs, Types, and Functions
The central type is `struct timestamp_expectation`, which stores a descriptive case name, expected `struct timespec64`, the raw extra-bit value, whether the most significant bit of the 32-bit timestamp is set, and whether the lower or upper bound of that 32-bit range should be used.

The `test_data[]` table covers negative 32-bit timestamps, nonnegative 32-bit timestamps, the two extra seconds bits used to extend ext4 timestamps past 2038, and nanosecond extraction from the high bits in the extra field. Constants such as `LOWER_MSB_0`, `UPPER_MSB_0`, `LOWER_MSB_1`, `UPPER_MSB_1`, and `MAX_NANOSECONDS` encode boundary raw values.

`timestamp_expectation_to_desc()` provides parameter names for KUnit output. `KUNIT_ARRAY_PARAM(ext4_inode, test_data, timestamp_expectation_to_desc)` generates the parameter set. `get_32bit_time()` maps the `msb_set` and `lower_bound` booleans to a representative signed 32-bit timestamp value. `inode_test_xtimestamp_decoding()` is the actual test body, and the suite is registered through `kunit_test_suites(&ext4_inode_test_suite)`.

## Control Flow
KUnit runs `inode_test_xtimestamp_decoding()` once for each row in `test_data[]`. For a row, the test derives the lower 32-bit timestamp with `get_32bit_time()`, converts both the lower timestamp and extra field to little-endian with `cpu_to_le32()`, and calls `ext4_decode_extra_time()`.

The test then compares decoded `tv_sec` and `tv_nsec` against the expected values using `KUNIT_EXPECT_EQ_MSG()`. The failure message includes the case name, msb flag, lower-bound flag, and extra bits, which makes boundary failures diagnosable without reading the table index.

## State and Persistence Behavior
There is no persistent state and no runtime filesystem state. All inputs are compile-time constants. The only state produced is KUnit test result state. Endianness conversion is included in the call site so the test exercises the same little-endian ABI shape as on-disk ext4 inode fields.

The expectations encode the ext4 timestamp persistence contract: the raw inode stores a 32-bit seconds field and an extra field whose low two relevant seconds bits extend time ranges while other bits encode nanoseconds. The suite verifies that ranges wrap from pre-1970 values through 2038, 2106, 2174, 2310, 2378, and 2446 boundaries as documented.

## Dependencies and Integration Points
The file includes KUnit, kernel time types, and `ext4.h`. Its only ext4 functional dependency is `ext4_decode_extra_time()`, which is normally consumed by inode deserialization macros in `inode.c`. It integrates with the kernel's KUnit module infrastructure via `kunit_test_suites`, `MODULE_DESCRIPTION`, and `MODULE_LICENSE`.

This test is a direct guard for inode timestamp reads. If ext4 changes the timestamp encoding macros, expands valid ranges, or modifies bit layout for extra inode timestamp fields, this table should be updated in lockstep with the documentation and decoder.

## Risks
The main risk is incomplete coverage rather than operational risk. The suite tests representative boundaries and nanosecond maximums, but it does not exhaustively test every combination of extra seconds bits and nanosecond bits. It also tests only decoding, not encoding through raw inode writeback macros. A mismatch between documentation and implementation could survive if both the selected test values and the decoder share an incorrect assumption outside the boundaries listed here.

Because `extra_bits` is a raw `u32`, rows such as `0xFFFFFFFF` test that unrelated high bits still produce `MAX_NANOSECONDS`, but the suite does not validate rejection or sanitization behavior because `ext4_decode_extra_time()` is a decoder, not a validator.

## Test Signals
Expected signals are parameterized KUnit pass/fail entries under the suite name `ext4_inode_test`. High-value regressions include off-by-one seconds at signed 32-bit boundaries, wrong wrap behavior when the low or high extra seconds bit is set, endian mistakes, nanoseconds exceeding `(1 << 30) - 1`, and divergence from the timestamp table in ext4 inode documentation. Complementary coverage would add encode/decode round trips through raw inode macros and randomized valid extra-bit combinations.
