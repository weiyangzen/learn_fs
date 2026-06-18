# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cper.c

Purpose: this file builds and buffers CPER records for amdgpu RAS/ACA error reporting. It encodes fatal uncorrectable errors, corrected/deferred runtime errors, and bad-page-threshold events into AMD/nonstandard CPER layouts and writes them into an in-memory amdgpu ring buffer.

Important APIs and functions: exported functions are `amdgpu_cper_entry_fill_hdr()`, section fillers for fatal/runtime/bad-page-threshold sections, `amdgpu_cper_alloc_entry()`, record generators `amdgpu_cper_generate_ue_record()`, `amdgpu_cper_generate_ce_records()`, `amdgpu_cper_generate_bp_threshold_record()`, ring writer `amdgpu_cper_ring_write()`, and lifecycle functions `amdgpu_cper_init()`/`amdgpu_cper_fini()`. Internal helpers build timestamps, section descriptors, severity mappings, detect CPER headers across ring wrap, compute entry sizes, and expose rptr/wptr to `amdgpu_ring`.

Control flow: record generation allocates a correctly sized CPER buffer, fills the header with signature, revision, timestamp, platform/creator IDs, notify type, and section count, fills one or more sections from ACA bank registers or fixed bad-page-threshold fields, writes the completed record to `adev->cper.ring_buf`, and frees the temporary buffer. The ring writer copies byte chunks into the dword ring, handles wrap, updates `wptr`, and advances `rptr` on overflow until it lands on the next CPER header.

State and persistence: CPER state lives under `adev->cper`: enable flag, unique atomic record ID, counters, locks, an array-sized maximum, and an `amdgpu_ring` used as transient storage. Records are not persisted by this file; they remain in the ring until overwritten or consumed by other RAS/debug paths. The record ID includes socket ID when SMUIO supports it.

Dependencies and integration: the implementation depends on `amd_cper.h` structures, ACA bank data from `amdgpu_aca`, RAS enablement checks, SR-IOV CPER policy, `amdgpu_ring_init()`/`amdgpu_ring_fini()`, kernel time conversion, GUID constants, and device identity fields. Call sites include ACA error handling and RAS EEPROM threshold flows.

Risks: ring wrap logic is sensitive to byte-versus-dword arithmetic and CPER record alignment. Allocation failures in record generation can leak a temporary record on later section-fill errors because some error paths return before freeing. `amdgpu_cper_fini()` checks ACA/SR-IOV enablement differently from `amdgpu_cper_init()` and may skip cleanup if enablement conditions drift. Hardcoded bad-page register fields must match consumers' interpretation.

Test signals: inject ACA UE/CE/deferred banks, generate bad-page-threshold records, validate CPER signatures/lengths/section offsets across ring wrap, test maximum section counts and records near `CPER_MAX_RING_SIZE`, exercise SR-IOV and non-SR-IOV enablement gates, and run memory-failure paths for allocation and ring initialization.
