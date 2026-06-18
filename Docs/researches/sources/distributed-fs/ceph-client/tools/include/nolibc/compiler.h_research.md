# sources/distributed-fs/ceph-client/tools/include/nolibc/compiler.h

## Purpose
Centralizes compiler feature detection and attributes used by nolibc headers.

## APIs, Types, and Functions
Defines `__nolibc_has_attribute`, `__nolibc_has_feature`, `__nolibc_aligned`, `__nolibc_aligned_as`, `__nolibc_naked`, stack-protector detection, `__no_stack_protector`, `__fallthrough`, standard-version helpers, optimizer barriers, and sanitizer-suppression attributes.

## Control Flow, State, and Persistence
All behavior is compile-time macro expansion. The header decides which attributes are available and exposes stable internal names so architecture and runtime code can annotate `_start`, stack-check code, packed/aligned data, and undefined-behavior-sensitive startup paths.

## Dependencies and Integration
Depends on GCC/Clang predefined macros, `__has_attribute`, `__has_feature`, and language version macros. It is included by architecture backends, CRT setup, and stack protector support.

## Risks and Test Signals
Risks are compiler-version feature probes that mis-detect support, attributes that differ subtly between GCC and Clang, and stack-protector suppression failing on startup code. Test signals are GCC and Clang builds, stack-protector-enabled nolibc programs, UBSan-enabled builds, and preprocessing checks for C89/C99/C11 modes.
