# sources/distributed-fs/ceph-client/drivers/powercap/dtpm_subsys.h

## Purpose
`dtpm_subsys.h` declares and assembles the enabled DTPM backend subsystem operations for the generic DTPM core.

## Important APIs, Types, And Functions
It declares `extern struct dtpm_subsys_ops dtpm_cpu_ops;` and `dtpm_devfreq_ops;`, then defines `struct dtpm_subsys_ops *dtpm_subsys[]` with entries conditional on `CONFIG_DTPM_CPU` and `CONFIG_DTPM_DEVFREQ`.

## Control Flow
The DTPM core includes this header and iterates `dtpm_subsys[]` during DT node setup, subsystem initialization, and subsystem exit. Compile-time configuration determines which setup/init/exit hooks are present.

## State, Persistence, And Dependencies
The array is static data in whichever translation unit includes the header, currently `dtpm.c`. There is no runtime mutation. Dependencies are the `struct dtpm_subsys_ops` definition from `linux/dtpm.h` and Kconfig symbols.

## Integration Points
This is the only list connecting generic DTPM hierarchy walking with CPU and devfreq backends. Adding another backend requires a new extern and conditional array entry.

## Risks
Defining a non-`static` array in a header would create duplicate symbols if included by multiple C files. It is currently included by `dtpm.c` only, but future includes could break linkage. The array has no sentinel; all loops use `ARRAY_SIZE(dtpm_subsys)`.

## Test Signals
Build all combinations of `CONFIG_DTPM_CPU` and `CONFIG_DTPM_DEVFREQ`, verify array size and linkage, ensure `dtpm.c` loops handle an empty array, and check no other C file includes this header.
