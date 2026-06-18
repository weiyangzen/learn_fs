# sources/distributed-fs/ceph-client/scripts/cc-version.sh

## Purpose
`cc-version.sh` identifies the C compiler family and canonical version, enforcing the kernel’s minimum supported GCC or LLVM version.

## APIs, Types, And Functions
Functions are `get_c_compiler_info()` and `get_canonical_version()`. It preprocesses a small snippet to print `GCC` or `Clang` plus version components, then consults `min-tool-version.sh`.

## Control Flow
The script captures the compiler identity using `$@ -E -P -x c -`, maps it to a minimum version category, canonicalizes installed and minimum versions, fails with diagnostics if too old, and prints `<name> <canonical-version>` on success.

## State And Persistence
No state is persisted; stdout is consumed by kbuild.

## Dependencies And Integration Points
It depends on C preprocessor predefined macros, POSIX shell, and `min-tool-version.sh`. It handles multiword compiler commands such as `ccache gcc`.

## Risks And Test Signals
Risks include unknown compiler frontends, nonstandard macro definitions, and unexpected version component formats. Test signals are expected output for GCC/Clang, failure for too-old compilers, and handling of wrapper commands.
