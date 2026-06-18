# sources/distributed-fs/ceph-client/arch/sparc/prom/cif.S

Purpose: provides SPARC64 assembly trampolines for calling IEEE-1275 Client Interface Firmware and handling PROM callbacks.

Important APIs/functions: exports `prom_cif_direct()` and `prom_cif_callback()`. Uses `p1275buf.prom_cif_handler` and `p1275buf.prom_callback`.

Control flow: `prom_cif_direct()` creates a register window, loads the CIF handler from `p1275buf`, preserves `%g4`-`%g6`, calls firmware with the argument array, restores globals, and returns. `prom_cif_callback()` reconstructs kernel thread/per-CPU globals, enters PROM world, calls the callback function pointer, exits PROM world, and returns the firmware callback result.

State and persistence: no owned memory state, but preserves/restores global registers and switches PROM/kernel world state.

Dependencies and integration points: used by `p1275.c`; depends on thread-info/per-CPU macros, PROM world switching, and the IEEE-1275 argument array convention.

Risks: global register preservation is critical because SPARC64 uses globals for kernel state. Callback path must reload thread/per-CPU bases before calling C code.

Test signals: early PROM calls, PROM callbacks, SMP boot with PROM access, and stress of PROM console/device-tree calls while interrupts and globals are sensitive.
