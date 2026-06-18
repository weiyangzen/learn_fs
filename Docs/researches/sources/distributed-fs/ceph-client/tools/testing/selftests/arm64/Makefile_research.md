# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/Makefile

Purpose: top-level dispatcher for arm64 kselftest subtargets.

Important APIs/types/functions: detects `ARCH`, sets `ARM64_SUBTARGETS` to `tags signal pauth fp mte bti abi gcs` on arm64/aarch64, configures CFLAGS/include paths/KHDR includes, exports `CFLAGS` and `top_srcdir`, and defines `all`, `install`, `run_tests`, `emit_tests`, and `clean` loops.

Control flow: each target iterates subdirectories, creates `OUTPUT` subdir, and invokes make in the subtarget with optional `FORCE_TARGETS` failure behavior. Non-arm64 emits no tests.

State and persistence: creates per-subtarget output directories.

Dependencies/integration: integrates arm64 subtests with top-level kselftest and header include layout.

Risks and test signals: host/cross compile depends on `ARCH` override. Empty `ARM64_SUBTARGETS` on non-arm64 prevents noisy emit output.
