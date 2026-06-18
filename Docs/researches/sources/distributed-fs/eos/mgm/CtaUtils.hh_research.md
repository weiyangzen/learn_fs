<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/CtaUtils.hh -->
# sources/distributed-fs/eos/mgm/CtaUtils.hh

Purpose: Declares `eos::mgm::CtaUtils`, a small utility surface used by CTA-aware MGM code, especially tape garbage-collection and WFE paths that parse CTA metadata, convert stored binary timestamps, and read bounded command output.

Important APIs/types/functions: The header defines exception types for parsing (`EmptyString`, `NonNumericChar`, `ParseError`, `ParsedValueOutOfRange`) and buffer conversion (`BufSizeMismatch`). `toUint64(std::string)` trims whitespace and parses unsigned decimal values in `CtaUtils.cc`. `divideAndRoundToNearest()` and `divideAndRoundUp()` are inline arithmetic helpers used by tape-GC rate/bin calculations. `bufToTimespec()` converts an exact-size byte buffer into a `timespec`, and `readFdIntoStr()` reads at most a caller-provided byte count from a file descriptor into a null-terminated `std::string`.

Control flow: This header is declaration-heavy; control flow is supplied by `CtaUtils.cc`. The inline division helpers are single-expression functions and assume valid nonzero divisors. The parser family signals input problems through typed exceptions rather than error codes, making callers responsible for catch/report behavior.

State and persistence behavior: `CtaUtils` is stateless and has no persistence. Its ABI-sensitive behavior is `bufToTimespec()`, because it interprets persisted or xattr-style bytes as the platform `timespec` layout.

Dependencies and integration points: It sits in the MGM namespace and includes logging, namespace, tape-GC cache/LRU headers, namespace metadata interfaces, and console protobuf headers, although the declarations themselves mostly require standard C++ and `timespec`. Call sites include `mgm/tgc/RealTapeGcMgm.cc`, `FreedBytesHistogram.cc`, `SmartSpaceStats.cc`, `AsyncUint64ShellCmd.cc`, and WFE archive-id parsing.

Risks: The inline division helpers do not guard `y == 0`. `readFdIntoStr()` uses signed `ssize_t maxStrLen`; negative values would be dangerous after unsigned conversion in the implementation, so callers must pass validated positive limits. `bufToTimespec()` is not portable across differing `timespec` layouts or endianness. Tests should cover whitespace-only parse failures, non-decimal input, max `uint64_t`, overflow, exact/mismatched timestamp buffers, file-descriptor read errors, and zero-divisor caller guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/CtaUtils.hh -->
