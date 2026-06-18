# File Research: sources/cow-pools/bcachefs-tools/linux/kstrtox.c

Implements Linux string-to-integer conversion helpers. It handles radix auto-detection, overflow detection, signed/unsigned conversion with range checks for multiple widths, and `kstrtobool()` for common boolean spellings.

Parsing allows one trailing newline and returns `-EINVAL` or `-ERANGE` without modifying result on failure.
