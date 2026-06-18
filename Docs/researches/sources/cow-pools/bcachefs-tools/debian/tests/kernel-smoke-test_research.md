# File Research: sources/cow-pools/bcachefs-tools/debian/tests/kernel-smoke-test

- Debian autopkgtest smoke test for installed kernel module and tools.
- Fails if `bcachefs` module is already loaded, then loads it, checks `modinfo`, lists the module file, and runs `bcachefs version`.
- Discovers sibling test scripts matching its basename, skips `.disabled`, runs each in a temporary directory, tracks failures, and cleans up.
