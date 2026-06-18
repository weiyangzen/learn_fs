<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sd.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sd.c

**Purpose:** `sclp_sd.c` implements Store Data support and exposes retrieved firmware data entities through `/sys/firmware/sclp_sd/`.

**Important APIs and functions:** It defines Store Data event/SCCB layouts, `struct sclp_sd_data`, listener objects keyed by event ID, and sysfs-backed `struct sclp_sd_file`. `sclp_sd_sync()` submits size, store-data, or halt operations and waits for immediate or asynchronous completion. `sclp_sd_store_data()` retrieves size, allocates vmalloc data, builds an ASCE for the target buffer, and fetches contents. `sclp_sd_file_create()` creates per-entity `data` and `reload` files.

**Control flow, state, and persistence:** Init registers for send/receive Store Data events, creates `/sys/firmware/sclp_sd`, creates the `config` entity with DI 3, and asynchronously loads its data. A request listener is added before submission so an asynchronous event with matching physical SCCB ID can complete it. Retrieved data persists in the `sclp_sd_file` until reload or object release.

**Dependencies and integration:** It depends on SCLP events, completions, async scheduling, firmware kobjects, vmalloc, base ASCE allocation/free, and sysfs binary attributes.

**Risks and test signals:** Risks include timeouts/interrupted requests requiring HALT, leaked data if HALT fails, listener races, asynchronous unsolicited events, large allocation sizes from firmware `dsize`, and reload blocking sysfs writes. Tests should cover no-data `-ENOENT`, immediate and async completion, timeout plus halt, data reads with offsets, reload uevents, and registration failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sd.c -->
