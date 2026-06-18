# sources/distributed-fs/ceph-client/include/linux/soc/pxa/cpu.h

Purpose: This PXA header provides CPU identification helpers for PXA210/25x/26x/27x/3xx/93x families and related Marvell variants.

Important APIs/types/functions: It defines variant-specific `__cpu_is_*` macros under config guards, maps them to public `cpu_is_*` helpers, and uses CPU ID/JTAG ID bit masks documented in the file comments. Disabled family configs make helpers compile to false.

Control flow: Platform code and drivers call the helpers to select silicon-specific code paths, errata, clocking, pin mux, and memory-controller behavior.

State and persistence: The helpers read or consume CPU ID values; no mutable state is stored here.

Dependencies and integration: Includes `asm/cputype.h` on ARM and integrates with PXA board/platform support, MFP, SMEMC, clocks, GPIO, and legacy drivers.

Risks and test signals: Conditional helpers can hide code at build time; wrong masks can classify a stepping incorrectly. Test build matrices for PXA25x/PXA27x/PXA3xx, runtime detection on each supported stepping, and users that gate register writes on these helpers.
