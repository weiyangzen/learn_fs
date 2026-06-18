# sources/distributed-fs/lizardfs/configure

## Purpose
This shell script is a compatibility wrapper that provides a traditional `./configure` entry point while delegating actual configuration to CMake.

## Important APIs, Types, and Functions
It accepts `--with-doc`, `--without-doc`, `--with-uraft`, and `--without-uraft`, sets defaults, creates `build-pack`, removes stale `CMakeCache.txt`, sets default environment-controlled official/RC build variables, runs CMake with packaging-oriented options, and writes a wrapper `Makefile` in the source root.

## Control Flow and State
The script changes to its own directory, creates an out-of-tree `build-pack`, and configures Release mode with tests off, install prefix `/`, docs according to parsed options, client library on, NFS-Ganesha off, uraft hard-coded on in the CMake invocation, and Polonaise off. It then writes Makefile targets that forward `all`, `clean`, and `install` to `build-pack`; `distclean` removes build artifacts and external gtest plus the wrapper Makefile.

## Dependencies and Integration Points
Debian packaging rules call this script. It depends on CMake, make, shell, and the top-level CMake project. Environment variables `LIZARDFS_OFFICIAL_BUILD` and `LIZARDFS_SET_RC_BUILD_NUMBER` feed package versioning.

## Risks and Edge Cases
The parsed `uraft` variable is not used; the CMake command always passes `-DENABLE_URAFT=YES`, so `--without-uraft` is ineffective. The script rewrites a source-root Makefile and removes external gtest on distclean. It assumes CMake can configure from `build-pack`.

## Test Signals
Running `./configure` should create `build-pack` and a forwarding Makefile. Debian package builds are the primary integration signal.
