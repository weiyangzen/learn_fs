# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.h

Purpose: this header exposes the small subset of Aldebaran debug helpers that other KFD/KGD bridge files reuse. It intentionally declares only `kgd_aldebaran_enable_debug_trap` and `kgd_aldebaran_set_wave_launch_mode`, leaving Aldebaran-specific disable, trap-override, and address-watch helpers private to the implementation file.

Important APIs: `kgd_aldebaran_enable_debug_trap(struct amdgpu_device *adev, bool restore_dbg_registers, uint32_t vmid)` returns a `SPI_GDBG_PER_VMID_CNTL` bitfield for enabling trap handling. `kgd_aldebaran_set_wave_launch_mode(struct amdgpu_device *adev, uint8_t wave_launch_mode, uint32_t vmid)` returns a bitfield with Aldebaran's launch mode encoded. Both APIs match the `kfd2kgd_calls` debug callback signatures, which makes them reusable by other GFX9.4.x tables.

Control flow and integration: `amdgpu_amdkfd_gc_9_4_3.c` includes this header and uses these two helpers in its `gc_9_4_3_kfd2kgd` table. `amdgpu_amdkfd_aldebaran.c` provides the definitions and also uses them in `aldebaran_kfd2kgd`. The header relies on declarations for `struct amdgpu_device`, `bool`, and fixed-width integer types being available through including translation units; it does not include those dependencies itself.

State and persistence: the header declares pure register-value helper APIs and owns no state. Persistent behavior is in the callers that write returned values into debug registers or save them in KFD debug bookkeeping.

Dependencies: this header is part of the AMDGPU driver private interface, not UAPI. It depends on the implementation file and on the broader KFD/KGD callback contract defined around `struct kfd2kgd_calls`.

Risks and test signals: because there is no include guard in the excerpted file, repeated inclusion is benign only because it contains declarations, but adding definitions or data here would be risky. Signature drift would break both Aldebaran and GC 9.4.3 tables at compile time. Tests are compile/link coverage plus debugger bring-up paths that exercise the shared enable and launch-mode callbacks.
