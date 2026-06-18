
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-core.c

Purpose: exports preserved OPAL firmware memory and CPU state from MPIPL as an ELF core file under sysfs.

Important APIs/types/functions: `struct opalcore_config` tracks CPU count, crashing PIR, CPU state buffer, PT_LOAD regions, ELF buffer, and file size. `create_opalcore()` builds ELF headers, PT_NOTE, and PT_LOAD descriptors. `read_opalcore()` serves the bin attribute. `opalcore_config_init()` discovers OPAL/CPU metadata via MPIPL tags. `release_core_store()` lets userspace release the exported core.

Control flow: `opalcore_init()` runs as an fs initcall, queries `/ibm,opal/dump` for MPIPL boot, retrieves OPAL and CPU metadata tags, parses region lists, validates CPU state layout, allocates a header buffer, builds ELF notes from HDAT register entries using `opal_fadump_read_regs()`, appends AUXV with OPAL entry point, creates `/sys/firmware/opal/mpipl/core`, and adds a compatibility symlink from the old location. Reads copy the header/note buffer first and then preserved OPAL memory via `__va()`.

State and persistence: global `oc_conf`, `opalcore_list`, OPAL metadata pointers, `mpipl_kobj`, and `kernel_initiated` persist until release or exit cleanup. Userspace can free memory by writing `1` to `release_core`.

Dependencies and integration points: integrates with OPAL MPIPL tags, sysfs/kobjects, ELF core note formats, FADump register parsing helpers, device-tree OPAL properties, and `/sys/firmware/opal`.

Risks: file correctness depends on firmware metadata versions, endian conversions, region counts capped by `MAX_PT_LOAD_CNT`, and preserved memory still being mapped. Cleanup has to remove sysfs files before freeing buffers. GDB interpretation relies on first `NT_PRSTATUS` representing the crashing CPU.

Test signals: MPIPL boot with OPAL metadata, valid ELF headers from sysfs `core`, GDB/core parsing, `release_core` cleanup, metadata version mismatch warnings, and behavior when CPU metadata is invalid.
