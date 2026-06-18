# sources/distributed-fs/ceph-client/scripts/decode_stacktrace.sh

## Purpose
`decode_stacktrace.sh` annotates Linux stack traces with source file and line information using `vmlinux`, module debug info, `nm`, and `addr2line`; it can also decode inline `Code:` lines through `decodecode`.

## Important APIs, Types, and Functions
Key functions are `find_module()`, `parse_symbol()`, `debuginfod_get_vmlinux()`, `decode_code()`, and `handle_line()`. It supports `-r <release>` lookup, `-R` return-address mode, module build IDs, optional debuginfod, Rust demangling via `llvm-cxxfilt` or `c++filt`, and tool prefix/suffix selection through `LLVM` and `CROSS_COMPILE`.

## Control Flow and State
Argument parsing resolves `vmlinux`, base path, module path, and release. If Bash associative arrays are available, symbol and module lookups are cached. The stdin loop strips CR, detects stack-symbol lines, `Code:` lines, and debuginfod version lines, then prints transformed or original lines. `parse_symbol()` resolves module/object, finds symbol base address via `nm`, adjusts return addresses unless `-R`, calls `addr2line -i`, strips base path, demangles Rust names, and rewrites the symbol token.

## Dependencies and Integration
It depends on Bash, GNU binutils or LLVM tools, `gdb` for release extraction, `find`, `sed`, optional debuginfod, and the sibling `decodecode` script.

## Risks and Test Signals
Stack trace tokenization is format-sensitive. Module paths with spaces are not robust. Missing debug info yields warnings and passthrough symbols. Test vmlinux-only traces, module traces, build-id debuginfod, inline frames, Rust symbols, `-R`, auto base path, and `Code:` continuation lines.
