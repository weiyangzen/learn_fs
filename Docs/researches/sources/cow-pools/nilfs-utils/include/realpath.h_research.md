# File Research: sources/cow-pools/nilfs-utils/include/realpath.h

Header for bundled canonical path resolver.

- Declares `myrealpath(const char *path, char *resolved_path, int m)`.
- The implementation is borrowed from util-linux mount code.
