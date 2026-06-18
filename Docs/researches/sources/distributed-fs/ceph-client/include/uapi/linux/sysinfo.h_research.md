# sources/distributed-fs/ceph-client/include/uapi/linux/sysinfo.h

## Purpose
Defines `struct sysinfo`, the userspace result shape for system uptime, load averages, memory, swap, process count, high memory, and memory unit scale.

## Important APIs, Types, and Constants
`SI_LOAD_SHIFT` gives the fixed-point load average shift. `struct sysinfo` fields include `uptime`, three `loads`, RAM and swap totals/free counts, shared and buffer memory, `procs`, m68k padding, high memory totals/free counts, `mem_unit`, and legacy libc5 padding.

## Control Flow, State, and Persistence
No code is present. Kernel fills this struct for `sysinfo(2)`. Values are a snapshot and not persistent; the layout and padding are ABI.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Integrates with `sysinfo(2)`, libc, monitoring tools, and memory-reporting utilities.

## Risks and Test Signals
Risks include load fixed-point misinterpretation, overflow if callers ignore `mem_unit`, and layout differences from `__kernel_long_t`. Test 32/64-bit struct size, load conversion, large-memory systems, and libc wrapper compatibility.
