# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Random.h

## Purpose
Declares random helper functions for kernel-module code.

## Important APIs and types
Exports `Random_getNextInt` and `Random_getNextInRange`. The API returns signed `int` values and defines `min`/`max` as inclusive range bounds.

## State, dependencies, integration
The header depends only on BeeGFS common definitions and leaves RNG implementation to the C file.

## Risks and test signals
Callers must enforce valid ranges. Unit tests or static checks should flag any `Random_getNextInRange` call where `max - min + 1` can be zero or overflow.
