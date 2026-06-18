<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/sclp_early_core.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/sclp_early_core.c

Purpose: Adapts the common SCLP early core implementation for the s390 boot decompressor and supplies a statically allocated early SCCB buffer.

Important APIs/types/functions: Includes `../../../drivers/s390/char/sclp_early_core.c`, defines page-aligned static `__sclp_early_sccb[EXT_SCCB_READ_SCP]`, and exports `sclp_early_setup_buffer()`.

Control flow: `sclp_early_setup_buffer()` passes the boot-local SCCB buffer to `sclp_early_set_buffer()`. All other SCLP early behavior comes from the included common driver source.

State and persistence: The SCCB buffer is static boot memory and must remain page-aligned and below 2GB, as required by SCLP early calls.

Dependencies and integration points: Used by startup and printk paths for SCLP reads, machine feature detection, memory info, and early console output.

Risks: If the included driver source adds dependencies unavailable in the boot environment, this wrapper can break. Buffer size, alignment, and addressability are firmware ABI requirements.

Test signals: Early SCLP read-info/storage-info calls, early console output, and builds after changes to the common SCLP early driver.

Source read size: 11 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/sclp_early_core.c -->
