# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-boot-vector.c

Purpose: manages the Octeon boot vector table used to start secondary cores or provide firmware-visible boot entries.

Important APIs and functions: `cvmx_boot_vector_init()` initializes a 1024-entry vector table with code/data fields expected by Octeon firmware. `cvmx_boot_vector_get()` locates an existing named bootmem allocation or allocates/initializes one, then returns a typed pointer to the table.

Control flow: callers request the table lazily. The function first searches bootmem for the reserved block, allocates it with required alignment/size if absent, initializes entries, and returns the mapped pointer.

State and persistence: the vector table lives in Octeon bootmem for the current boot and may be shared with firmware/other CPUs. It is not persisted across power cycles.

Dependencies and integration points: depends on Octeon executive bootmem APIs and `cvmx_boot_vector` ABI structures. It integrates with SMP boot and low-level Octeon firmware handoff.

Risks and test signals: allocation failure or ABI mismatches can prevent secondary CPU startup. Test by verifying bootmem allocation logs, SMP bring-up, vector table contents, and behavior on systems with preexisting firmware-allocated tables.
