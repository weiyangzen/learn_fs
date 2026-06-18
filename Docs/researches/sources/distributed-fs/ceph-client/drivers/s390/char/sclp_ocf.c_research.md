<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ocf.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ocf.c

**Purpose:** `sclp_ocf.c` receives SCLP OCF communication-parameter events and exposes HMC network and CPC name information under firmware sysfs.

**Important APIs and functions:** `sclp_ocf_handler()` parses nested GDS vectors/subvectors for network ID and CPC name. `sclp_ocf_cpc_name_copy()` is exported for in-kernel users needing the raw EBCDIC CPC name. Sysfs read attributes are `cpc_name` and `hmc_network` under `/sys/firmware/ocf/`.

**Control flow, state, and persistence:** The event handler searches for GDS blocks `0x9f00`, `0x9f22`, `0x81`, then subkeys 1 and 2. It updates global `hmc_network` in ASCII and `cpc_name` in EBCDIC under `sclp_ocf_lock`, then schedules a work item that emits `KOBJ_CHANGE` on the OCF kset. Data persists in those globals until a later OCF event overwrites it.

**Dependencies and integration:** It uses SCLP event type `EVTYP_OCF`, GDS traversal helpers from `sclp.h`, EBCDIC conversion, firmware ksets, workqueues, and spinlocks.

**Risks and test signals:** Risks include trusting vector lengths, off-by-one size use when copying subvector payloads, mixed ASCII/EBCDIC storage semantics, and event delivery before sysfs setup. Tests should cover valid nested events, missing vector levels, sysfs rendering, exported raw copy, KOBJ_CHANGE emission, and concurrent reads during event updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ocf.c -->
