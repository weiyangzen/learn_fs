# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-fadump.c

Purpose: Implements RTAS firmware-assisted dump operations for PowerVM, bridging generic fadump core logic with RTAS `ibm,configure-kernel-dump` structures and firmware-provided dump data.

Important APIs/types/functions: Uses static `fdm` and `fdm_active`, and implements `rtas_fadump_init_mem_struct()`, register/unregister/invalidate/process/region-show/trigger/max-region ops, CPU register parsing helpers, `rtas_fadump_build_cpu_notes()`, and `rtas_fadump_dt_scan()`.

Control flow: Device-tree scan detects fadump support and active dumps, captures firmware section sizes, and installs `fadump_ops`. Registration builds a dump memory structure with CPU state, HPTE, boot memory, and optional parameter sections, then calls RTAS with busy-delay handling. Capture kernel processing validates completed sections, parses firmware `REGSAVE` CPU register data into ELF notes, overlays exact crash CPU registers from the fadump header, and updates the vmcore header.

State and persistence: `fdm` is the registration structure for future crashes; `fdm_active` points to firmware-preserved active dump metadata from the flattened device tree. Generic `fw_dump` carries reservation, boot-memory, CPU-note, and active/registered state.

Dependencies and integration points: Depends on generic fadump internals, RTAS calls, OF flat tree properties, memblock/crash dump plumbing, ELF note generation, and `rtas-fadump.h` layout definitions.

Risks: Section counts and exact structure size must match firmware expectations. Active-dump pointer address handling is subtle. CPU register parser trusts firmware sentinels and can run off if malformed. Busy-delay loops currently have TODOs for upper time limits.

Test signals: Fadump register/unregister/invalidate, active dump capture boot, malformed or incomplete sections, CPU note generation for multiple CPUs, parameter-area preservation, non-contiguous reserved memory error, and RTAS busy/error status mapping.

Source read size: 649 lines, 19570 bytes.
