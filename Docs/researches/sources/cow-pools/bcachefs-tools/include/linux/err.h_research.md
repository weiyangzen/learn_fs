# File Research: sources/cow-pools/bcachefs-tools/include/linux/err.h

This header ports kernel error-pointer helpers. `MAX_ERRNO` is `4095`, and `IS_ERR_VALUE()` detects encoded error pointers near the top of address space.

It defines `ERR_PTR()`, `PTR_ERR()`, `IS_ERR()`, `IS_ERR_OR_NULL()`, `ERR_CAST()`, and `PTR_ERR_OR_ZERO()`. The comment explains why the kernel pointer-encoding convention remains usable in user space, especially on x86_64 where the high address range is outside normal user mappings.
