# sources/compression/zstd/lib/install_oses.mk

## Purpose
`install_oses.mk` centralizes OS detection and the list of operating systems for which the zstd library makefiles support install targets.

## Important Variables
- `UNAME := $(shell sh -c 'MSYSTEM="MSYS" uname')` runs `uname` with `MSYSTEM` forced to `MSYS`, improving MSYS/Cygwin-style detection consistency.
- `INSTALL_OS_LIST ?= ...` defines the default supported OS patterns: Linux, Darwin, GNU variants, BSDs, SunOS, Haiku, AIX, MSYS_NT%, and CYGWIN_NT%.

## Control Flow
The file is intended to be included by other makefiles. Inclusion evaluates `UNAME` immediately and provides a default `INSTALL_OS_LIST` only if the including environment has not already set it.

## State And Persistence
There is no file output or persistent state. The included make variables affect target availability and conditional logic in parent makefiles.

## Dependencies And Integration Points
It depends on `sh` and `uname` being available. Parent makefiles can compare `$(UNAME)` against `$(INSTALL_OS_LIST)` to decide whether install/uninstall targets are valid. The `?=` assignment allows packaging systems or callers to override the OS allowlist.

## Risks And Edge Cases
- OS detection is pattern-based and may miss newer or niche systems unless `INSTALL_OS_LIST` is overridden.
- Forcing `MSYSTEM="MSYS"` changes `uname` behavior intentionally but can surprise callers expecting their existing MSYS flavor.
- Systems without POSIX `sh`/`uname` cannot evaluate `UNAME` as written.

## Test Signals
Makefile tests should include this file under representative `uname` outputs, verify `INSTALL_OS_LIST` override behavior, and check install-target conditionals on Linux, macOS, BSD, MSYS, and Cygwin environments.
