# sources/distributed-fs/ceph-client/include/acpi/platform/acgccex.h

Purpose: Provides extra GCC cleanup after headers are included, currently to avoid buggy macro versions of `strchr()` in some toolchains.

Important APIs, types, and functions: Undefines `strchr` if it is a macro. No functions or types are exported.

Control flow: Single preprocessor conditional executes at include time.

State and persistence: No state.

Dependencies and integration points: Included by `acenvex.h` for GCC builds. It protects ACPICA utility code such as getopt parsing from problematic libc/compiler macro substitutions.

Risks and test signals: Risks are subtle compile failures if `strchr` remains macro-expanded or if undefining it conflicts with a target C library expectation. Test ACPICA utility builds on GCC/libc combinations known to define `strchr` as a macro.
