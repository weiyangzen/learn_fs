# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-boot-vector.h

## Purpose
This header defines the Octeon boot-vector table ABI used to redirect a core after NMI. It gives one vector entry per possible MIPS CPUNum and exposes the lookup function for code that installs per-core secondary entry points.

## Important APIs, Types, and Functions
`OCTEON_BOOT_MOVEABLE_MAGIC1` identifies the movable boot-bus vector code. `struct cvmx_boot_vector_element` contains `target_ptr` plus three application-owned argument slots, `app0`, `app1`, and `app2`. `cvmx_boot_vector_get()` returns the vector table base or `NULL` if the table cannot be obtained.

## Control Flow
Callers obtain the vector table, fill the indexed entry for a target core, then trigger NMI or a boot-vector mechanism. When the vector code runs, it transfers execution to `target_ptr` for that core while preserving most general-purpose registers as described in the file comments.

## State and Persistence Behavior
The vector table is persistent shared boot memory or boot-bus-installed state. Application argument fields remain untouched by vectoring code. The vectoring path clobbers CP0_DESAVE and, on Octeon II and later, CP0_KScratch2; older cores also clobber `k1`.

## Dependencies and Integration Points
It depends on `asm/octeon/octeon.h` and the implementation in `cvmx-boot-vector.c`. It integrates with SMP bring-up, NMI-based core release, crash/debug paths, and bootloader-provided low-level vector code.

## Risks
The table index uses CPUNum, which is not always a compact Linux CPU number on multi-node systems. A bad `target_ptr` or stale argument slot can send a core into invalid code during NMI. Callers must account for documented scratch register clobbering and address-space expectations for kseg0/xkphys target pointers.

## Test Signals
Signals include successful secondary-core release, correct target entry on sparse-core systems, no register corruption beyond documented scratch registers, valid behavior on pre-Octeon-II and newer CPUs, and failure handling when `cvmx_boot_vector_get()` returns `NULL`.
