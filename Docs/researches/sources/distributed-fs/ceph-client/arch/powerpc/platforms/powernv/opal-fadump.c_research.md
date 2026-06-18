
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-fadump.c

Purpose: implements OPAL-backed firmware-assisted dump registration, preservation, crash processing, CPU note construction, and MPIPL trigger behavior for PowerNV.

Important APIs/functions: `opal_fadump_dt_scan()` discovers support and active dumps. `opal_fadump_init_mem_struct()`, `opal_fadump_setup_metadata()`, `opal_fadump_register()`, `opal_fadump_unregister()`, `opal_fadump_invalidate()`, `opal_fadump_process()`, `opal_fadump_region_show()`, and `opal_fadump_trigger()` populate `struct fadump_ops`. Under `CONFIG_PRESERVE_FA_DUMP`, `opal_fadump_dt_scan()` only preserves memory above the firmware boot-memory tag.

Control flow: normal build scans `/ibm,opal/dump`, validates firmware load areas against `OPAL_FADUMP_MIN_BOOT_MEM`, sets FADump support and max copy size, detects MPIPL boot, retrieves kernel and CPU metadata tags, validates metadata version/registered regions, marks dump active, and reconstructs boot memory configuration. Registration initializes kernel metadata in reserved dump memory, registers firmware tags, and adds each boot memory range through `opal_mpipl_update(OPAL_MPIPL_ADD_RANGE)`. Processing reads crash header and firmware CPU state, builds ELF notes from HDAT register entries, and updates the vmcore header. Trigger records crashing PIR and requests `OPAL_REBOOT_MPIPL`.

State and persistence: metadata is deliberately placed in reserved memory and registered with OPAL so the capture kernel can retrieve it. Runtime globals track active kernel metadata, CPU metadata, and the writable metadata structure.

Dependencies and integration points: generic FADump internals, OPAL MPIPL APIs, flat device tree scanning, crash dump/vmcore note helpers, `opal-fadump.h` HDAT parsing, and optional OPAL core export via `kernel_initiated`.

Risks: metadata format/version mismatch can corrupt vmcore interpretation. Partial registration is accepted on `OPAL_RESOURCE` but warns about unsaved regions. CPU-state fallback may include only crashing CPU registers. The preserve-only build has different semantics and must not invalidate preserved memory.

Test signals: FADump registration/unregistration, MPIPL crash and capture boot, vmcore CPU notes, preserve mode memory reservation, region display output, firmware load-area rejection, and invalid CPU metadata fallback.
