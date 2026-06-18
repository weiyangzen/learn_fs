## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_hwdb.c

### Purpose
`etnaviv_hwdb.c` provides a small built-in hardware database of known Vivante GPU identities. It corrects or fills chip feature and specification fields when hardware registers are incomplete, unreliable, or use wildcard product/customer/ECO ids.

### Important APIs, Types, And Functions
The file defines `etnaviv_chip_identities[]`, an array of `struct etnaviv_chip_identity` records, and exposes `etnaviv_fill_identity_from_hwdb()`.

### Control Flow
`etnaviv_fill_identity_from_hwdb()` compares the already-read model, revision, product id, customer id, and ECO id against each table entry. Product, customer, and ECO fields in the table may be `~0U` as wildcards. On match, it copies the full identity record into `gpu->identity`, restores the originally read id values for wildcarded fields, and reports success.

### State, Persistence, And Dependencies
There is no mutable state. The persistent effect is the replacement of `gpu->identity` during `etnaviv_hw_identify()` before raw feature-register fallback. The file depends only on `etnaviv_gpu.h`.

### Integration Points
`etnaviv_gpu.c` calls this after model/revision quirks and before reading feature registers. The resulting identity drives get-param UAPI responses, MMU/security decisions, clock-gating workarounds, scheduler behavior, perfmon domain availability, and userspace driver feature selection.

### Risks
Incorrect table entries can expose unsupported features or hide supported ones, causing userspace command streams or kernel workarounds to mismatch hardware. Wildcards are useful but increase the chance of overmatching. New cores require careful validation against register dumps and userspace expectations.

### Test Signals
Tests should compare known hardware register dumps against expected identity fields, cover wildcard preservation of product/customer/ECO ids, verify no unintended matches for close revisions, and validate userspace feature queries on each table-supported model.
