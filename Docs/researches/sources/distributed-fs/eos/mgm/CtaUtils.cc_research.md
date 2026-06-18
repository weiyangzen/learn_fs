# sources/distributed-fs/eos/mgm/CtaUtils.cc

## Purpose

`CtaUtils.cc` implements small EOS MGM utility functions used around CTA/tape integration: strict decimal `uint64_t` parsing, binary `timespec` reconstruction, and bounded file-descriptor reads into strings.

## Important APIs, Types, and Functions

`CtaUtils::toUint64(std::string)` trims the input, rejects empty strings, rejects any non-digit character, calls `std::stoull`, and maps exceptions to domain-specific `EmptyString`, `NonNumericChar`, `ParseError`, and `ParsedValueOutOfRange`. `CtaUtils::bufToTimespec(const std::string&)` checks `buf.size() == sizeof(timespec)`, then `memcpy`s into a `timespec`. `CtaUtils::readFdIntoStr(int fd, ssize_t maxStrLen)` rejects requests above a 4 GiB boundary, allocates a NUL-terminated buffer, reads once from the fd, throws on read errors, and returns a string copy.

## Control Flow

Each helper is synchronous and exception-based. `toUint64()` performs validation before conversion. `bufToTimespec()` fails before copying on size mismatch. `readFdIntoStr()` performs a single `read()` call, then NUL-terminates at either `readRc` or `maxStrLen`.

## State and Persistence Behavior

There is no stored state. `readFdIntoStr()` advances the supplied file descriptor's read offset and allocates temporary memory.

## Dependencies and Integration Points

It depends on `common/StringUtils.hh` for trimming, `mgm/CtaUtils.hh` for class and exception declarations, POSIX `read`, C++ strings/streams/limits/memory, and platform `timespec` ABI size.

## Risks

`readFdIntoStr()` reads only once, so it may return partial data from pipes, sockets, or large files even when more data is available. Negative `maxStrLen` is not explicitly rejected before allocation arithmetic. `bufToTimespec()` serializes native `timespec` layout, so data is not portable across architectures or libc ABIs. `toUint64()` rejects plus signs and whitespace inside values by design. The error text in `bufToTimespec()` says "does match" where it means "does not match."

## Test Signals

Tests should cover trim-only empty strings, non-digit rejection, maximum `uint64_t`, overflow, leading zeroes, valid and invalid `timespec` buffer sizes, native round-trip `timespec`, fd read errors, zero-length reads, partial pipe reads, and negative or huge `maxStrLen`.
