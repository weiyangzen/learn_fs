# sources/distributed-fs/ceph-client/drivers/misc/ocxl/mmio.c

Purpose: provides exported helper APIs for 32-bit and 64-bit global AFU MMIO reads, writes, set-bit, and clear-bit operations with caller-selected endian handling.

Important APIs and functions: exported symbols are `ocxl_global_mmio_read32()`, `ocxl_global_mmio_read64()`, `ocxl_global_mmio_write32()`, `ocxl_global_mmio_write64()`, `ocxl_global_mmio_set32()`, `ocxl_global_mmio_set64()`, `ocxl_global_mmio_clear32()`, and `ocxl_global_mmio_clear64()`. They operate on `struct ocxl_afu`, using `afu->global_mmio_ptr` and `afu->config.global_mmio_size`.

Control flow: each function checks that the requested offset leaves enough room for the access width, normalizes `OCXL_HOST_ENDIAN` to big-endian on big-endian builds, then selects `readl/readq/writel/writeq` or their `_be` variants. Set/clear helpers perform read-modify-write cycles.

State and persistence: no persistent state is held by this file. All state changes are direct MMIO writes to AFU global registers.

Dependencies and integration points: depends on OCXL AFU config and `enum ocxl_endian` from public/internal headers. These helpers are exported for other kernel OCXL clients.

Risks and test signals: offset checks can underflow if `global_mmio_size` is smaller than access width, so boundary tests should include zero and sub-width sizes. Read-modify-write helpers are not serialized here; callers must handle concurrent register updates. `ocxl_global_mmio_clear64()` performs a second unconditional `writeq(tmp, ...)` after the endian switch, which can duplicate the write and force little-endian/non-BE access even after a big-endian clear path; regression tests should cover BE behavior. MMIO fault-injection tests should verify no out-of-range access occurs.
