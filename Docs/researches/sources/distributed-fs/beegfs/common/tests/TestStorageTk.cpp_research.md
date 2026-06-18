# sources/distributed-fs/beegfs/common/tests/TestStorageTk.cpp

Purpose: This test verifies `StorageTk::findLongestMountedPrefix()`, especially parsing of `/proc/mounts`-style escaped path components and selection of the longest valid mount prefix.

Important APIs/types/functions: The file defines `FULL_SET` as the escaped form used in mounts files and `FULL_SET_RAW` as the raw path component. The test feeds a synthetic mounts stream into `StorageTk::findLongestMountedPrefix()` and compares returned `Mount{device, mountpoint, fstype}` values.

Control flow: The test first checks rejection of empty paths, relative paths, and failed streams. It then uses a multi-line mounts fixture containing `/`, `/test/foo/bar`, `/test/fo`, an escaped all-byte component, and `/test/foo`. It verifies fallback to root for a nonmatching sibling, exact longest match for nested paths, exact match for `/test/foo`, and escaped mount decoding for raw special characters both at the mountpoint and beneath it.

State and persistence behavior: No disk is touched; all persistence-like behavior is simulated through `std::stringstream`. The test protects code that reads real mount tables and affects metadata storage compatibility decisions elsewhere.

Risks and test signals: The key risk is path-prefix false positives, for example treating `/test/fo` as a prefix of `/test/foo`, or mishandling octal escapes. Coverage is good for matching and decoding but does not cover malformed mount lines, whitespace in device names, or duplicate mount ordering beyond this fixture.
