<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/usage.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/usage.cc

## Purpose
This example program demonstrates how to use the `crcutil_interface::CRC` wrapper. It constructs CRC instances, prints their properties, computes CRCs in several ways, validates rolling and algebraic CRC operations, stores CRC bytes into a message buffer, and deletes the objects.

## Important functions and data
- `kRollWindow` is `4`, used for rolling CRC examples.
- `kTestData` is the sample message `"abcdefgh"`.
- `kTestDataHead` and `kTestDataTail` split the message for incremental and concatenation demonstrations.
- `xprintf` wraps `vprintf`, flushes stdout, and avoids GCC warnings about `long long` format handling in older GCC versions.
- `Show(const CRC*)` contains the full demonstration sequence.
- `ShowAndDelete(CRC*)` calls `Show` then `Delete`.
- `main` creates two 32-bit canonical CRC instances with different reversed polynomials and rolling start values, using `CRC::IsSSE42Available()` to allow the CRC32C hardware path where applicable.

## Control flow
`main` calls `CRC::Create` twice, first for polynomial `0xEB31D82E` and then for CRC32C/Castagnoli polynomial `0x82f63b78`, both degree 32. Each pointer is passed to `ShowAndDelete`. `Show` starts by reading and printing polynomial, degree, canonical value, rolling start value, rolling window length, and self-check value.

The computation section calculates a CRC over the whole message, then recomputes it incrementally over head and tail chunks. It compares `CrcOfZeroes` against an actual zero-filled buffer. For rolling CRC, it prints expected values by direct computation for each four-byte window and actual values by `RollStart` plus repeated `Roll`. It demonstrates `ChangeStartValue` by converting a CRC computed with start 0 to the value expected with start 1. It demonstrates `Concatenate` by combining CRCs of two message parts. Finally it demonstrates `StoreComplementaryCrc`, `StoreCrc`, and `CrcOfCrc` by appending bytes to a buffer and recomputing.

## State and persistence behavior
The program has only stack/local state and stdout output. `buffer` is reused for zero-data and message-plus-CRC tests. CRC objects allocate internal implementation state through `CRC::Create` and are released by `Delete` in `ShowAndDelete`. No files are read or written.

## Dependencies and integration points
The program includes `std_headers.h` and `interface.h`, depending on the facade rather than crcutil internals. It requires C varargs and stdio functions made available by `std_headers.h`. It links with `examples/interface.cc` and the crcutil implementation headers/templates pulled in there. As an example, it is also a practical smoke test for the facade and for build-system compiler/linker configuration.

## Risks and edge cases
`ShowAndDelete` does not check for `NULL`, so if `CRC::Create` rejects arguments or allocation fails, `Show` will dereference a null pointer. The output is demonstrative rather than assertive; mismatches are printed as `expected` values but do not cause a nonzero exit. Format strings assume `UINT64` is compatible with `%llx` and `%llu`, which matches the typedef here but is less portable if changed. The rolling expected loop iterates `i <= kRollWindow` for the eight-byte test string and four-byte window, which is correct for this sample but tied to the constants.

## Test signals
Run the example and manually or script-check that full and incremental CRCs match, `CrcOfZeroes` matches actual zero-buffer computation, rolling actual values match expected values, `ChangeStartValue` and `Concatenate` match direct recomputation, complementary CRC produces zero, and `CrcOfCrc` equals the predicted constant. Converting the printed comparisons into assertions would make this a stronger automated regression test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/usage.cc -->
