# File Research: sources/cow-pools/bcachefs-tools/src/dump_stack.rs

Exports `bch2_demangle` as a C ABI helper for demangling Rust/C++ Itanium-style symbol names.

Behavior:
- Accepts input C string and output buffer.
- Returns 0 on null pointers, zero output length, or invalid UTF-8.
- Uses `rustc_demangle::demangle` with `{:#}` formatting to suppress legacy Rust hash suffixes.
- Copies at most `out_len - 1` bytes and NUL-terminates.
- Returns bytes written, excluding the NUL.

Potential concerns:
- The function is unsafe and trusts the C caller that input and output buffers are valid for the specified lengths.
- It returns 0 for invalid UTF-8, which is also a valid result for an empty demangled string.
