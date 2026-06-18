# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/config

Purpose: kselftest config fragment identifying kernel options needed for pstore tests.

Important APIs and functions: not executable code. It requests `CONFIG_MISC_FILESYSTEMS`, `CONFIG_PSTORE`, `CONFIG_PSTORE_PMSG`, `CONFIG_PSTORE_CONSOLE`, and modular `CONFIG_PSTORE_RAM`.

Control flow: consumed by kselftest/kernel config tooling rather than runtime scripts.

State and persistence: no runtime state.

Dependencies and integration: integrates with selftest config collection to help build kernels that expose pstore, pmsg, console, and ramoops backend capabilities.

Risks and test signals: `CONFIG_PSTORE_RAM=m` still requires module loading and backend registration at runtime. Missing backend will be caught by `common_tests`.
