# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cper.h

Purpose: this header defines the amdgpu CPER subsystem's constants, state container, CPER record types, and external API used by ACA/RAS code to generate and buffer CPER entries.

Important APIs/types: constants describe maximum record count and ring size plus header/section sizes and section-offset macros. `enum amdgpu_cper_type` distinguishes runtime, fatal, boot, and bad-page-threshold records. `struct amdgpu_cper` stores enablement, a unique ID counter, locks, lifetime counters, write pointer, an entry pointer array, and an `amdgpu_ring` ring buffer. Public functions cover header/section filling, CPER allocation, UE/CE/bad-page record generation, ring writing, and init/fini.

Control flow and integration: RAS/ACA callers include this header to create records after hardware error collection. The implementation computes layout from the macros here, so the offset macros are part of the ABI between record allocation, section filling, and ring readers.

State and persistence: all declared state is per-device and in memory. `unique_id` is atomic to tolerate multiple producers, while `cper_lock` and `ring_lock` separate high-level CPER state from ring-buffer mutation. No on-disk persistence is specified.

Dependencies: the header includes `amd_cper.h` for CPER structures and `amdgpu_aca.h` for ACA bank types. It also relies on core amdgpu declarations for `struct amdgpu_device` and ring support.

Risks: layout macros assume CPER sections are packed in header, descriptor array, then homogeneous section arrays; mixed section types would require new layout rules. The `ring` pointer array and `count` fields are declared but the current implementation primarily uses `ring_buf`, so unused state can confuse future changes. `CPER_MAX_RING_SIZE` and `CPER_MAX_ALLOWED_COUNT` are fixed compile-time limits.

Test signals: compile-time structure size/offset checks, CPER parser compatibility tests, and RAS injection paths should verify that each exported generator creates records matching the layout described by this header.
