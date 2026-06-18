# sources/distributed-fs/lizardfs/src/common/human_readable_format_unittest.cc

Purpose: tests SI and IEC byte-count formatting.

Important APIs/types/functions: `HumanReadableFormatTests.ConvertToSi` and `ConvertToIec`.

Control flow: tests assert exact strings for zero/small values, base boundaries, decimal rounding, petabyte/exabyte outputs, and `uint64_t` maximum.

State and persistence: none beyond test inputs.

Dependencies and integration: includes `human_readable_format.h` and `gtest`.

Risks: only byte count functions are covered; `ipToString`, `timeToString`, and `bpsToString` have no direct tests here.

Test signals: strong expected-output regression coverage for unit suffix and rounding choices.
