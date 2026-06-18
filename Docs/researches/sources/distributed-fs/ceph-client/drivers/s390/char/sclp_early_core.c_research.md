<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early_core.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early_core.c

**Purpose:** This file implements raw early-boot SCLP command execution, early console printing, event-mask setup, and early read-SCP/storage information helpers before the main interrupt and request-queue infrastructure is available.

**Important APIs and functions:** `sclp_early_cmd()` issues a `servc` and waits for the service-signal interrupt using `sclp_early_wait_irq()`. `sclp_early_set_event_mask()`, `sclp_early_con_check_linemode()`, and `sclp_early_con_check_vt220()` manage early masks. `__sclp_early_printk()`, `sclp_early_printk()`, and `sclp_emergency_printk()` emit line-mode and VT220 messages. `sclp_early_read_info()`, `sclp_early_get_info()`, `sclp_early_get_memsize()`, `sclp_early_get_hsa_size()`, and `sclp_early_read_storage_info()` provide boot discovery data.

**Control flow, state, and persistence:** The preserved `sclp_early_sccb` buffer is reused for all early commands. Read-SCP information is copied into `sclp_info_sccb` once valid. Early printing temporarily enables event masks, writes one or both console formats, then disables masks again. Mask setup retries in 4-byte compatibility mode when response `0x74f0` is returned.

**Dependencies and integration:** It manipulates lowcore PSWs/control registers directly, uses early physical memory constraints, EBCDIC conversion, SCLP message structures from `sclp_rw.h`, and physmem range reporting.

**Risks and test signals:** Risks include waiting for the wrong external interrupt, using a buffer not below 2 GiB/page-aligned, early console output after normal SCLP init has begun, and storage-info failures clearing discovered ranges. Tests should cover forced and normal read-SCP commands, mask compatibility fallback, emergency printing on stopped CPUs, early memory-size calculation, and storage range enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early_core.c -->
