# sources/distributed-fs/ceph-client/scripts/check-uapi.sh

## Purpose
`check-uapi.sh` checks UAPI header backward compatibility between a base ref or dirty tree and a past Git ref by compiling installed headers and comparing ABI with `abidiff`.

## APIs, Types, And Functions
Key functions include `gen_suppressions()`, `tree_is_dirty()`, `get_file_list()`, `add_to_incompat_list()`, `do_compile()`, `run_make_headers_install()`, `install_headers()`, `check_uapi_files()`, `check_individual_file()`, `compare_abi()`, `check_deps()`, `run()`, and `main()`.

## Control Flow
CLI options choose base/past refs, job count, error log, ambiguity handling, quiet, and verbose modes. The script validates tools and refs, creates a temp dir, generates libabigail suppressions, installs UAPI headers for both refs, diffs the installed trees, then compiles each past-ref header into a debug shared object for both versions and runs `abidiff`. Checks run in bounded parallel background jobs.

## State And Persistence
State lives in a temporary directory containing header installs, compiled `.bin` files, logs, suppressions, and incompatibility lists. The temp dir is removed on exit. Optional error logs persist at the caller-provided path.

## Dependencies And Integration Points
It depends on Git, make `headers_install`, abigail `abidiff` >= 2.4, a C compiler, architecture headers, `usr/include/Makefile`, and libdw for clang. It integrates with UAPI review, CI, and architecture-specific header installation.

## Risks And Test Signals
Risks include long runtime, tool version sensitivity, suppressed changes hiding real ABI breaks, and compile failures from headers that need exclusion. Test signals are success when only additive UAPI changes occur, failure logs for removed/changed ABI, and prerequisite exit code when tools or refs are invalid.
