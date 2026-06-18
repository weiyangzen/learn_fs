# File Research: sources/block-storage/mdadm/coverity-gcc-hack.h

## Purpose
`coverity-gcc-hack.h` supplies fake `_Float*` typedefs for Coverity's GCC model on x86_64.

## Behavior
When outside the kernel, on x86_64, and Coverity reports GCC version at least 7.0, it typedefs `_Float128`, `_Float64`, `_Float32`, and extended variants as vector-sized `float` types.

## Integration Notes
This is a static-analysis compatibility shim, not runtime mdadm logic.
