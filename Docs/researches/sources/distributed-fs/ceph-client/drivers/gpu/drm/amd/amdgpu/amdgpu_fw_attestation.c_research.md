# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fw_attestation.c

## Purpose
`amdgpu_fw_attestation.c` exposes PSP firmware-attestation records through a debugfs binary read file on supported discrete GPUs. It validates an attestation database header in VRAM and streams valid fixed-size firmware records to userspace.

## Important APIs, types, and functions
The public initializer is `amdgpu_fw_attestation_debugfs_init()`. Internal data layouts are `struct FW_ATT_DB_HEADER` and `struct FW_ATT_RECORD`. Core logic is in `amdgpu_fw_attestation_debugfs_read()` and support gating is in `amdgpu_is_fw_attestation_supported()`.

## Control flow
Debugfs initialization rejects unsupported devices, then creates `amdgpu_fw_attestation` under the primary DRM minor debugfs root. Reads require a user buffer at least as large as one record, stop at the 4 KiB maximum table size, ask PSP for the attestation-records address, convert that address to a VRAM offset, and on position zero read the header and validate the cookie. Each read then fetches one record after the header plus current file position, stops on the first invalid record, copies a valid record to userspace, advances the file position by one record, and returns the record size.

## State and persistence behavior
The records are stored in VRAM by PSP/firmware and are read on demand. The driver keeps no cache. File position controls iteration through the table during a debugfs read sequence.

## Dependencies and integration points
It depends on debugfs, PSP `psp_get_fw_attestation_records_addr()`, VRAM access through `amdgpu_device_vram_access()`, AMDGPU IP-version/ASIC helpers, and DRM logging. It excludes APUs, MP0 14.0.2/14.0.3, and ASICs older than Sienna Cichlid.

## Risks and edge cases
The file exposes raw binary records, so readers must know the structure layout. Bounds checking uses the maximum table size and current position, but corrupted firmware data can still stop iteration early through invalid cookie or record-valid flags. VRAM address conversion assumes the PSP-provided address lies in VRAM. `copy_to_user()` failures return `-EINVAL` rather than `-EFAULT`.

## Test signals
Signals include debugfs file presence only on supported ASICs, valid cookie acceptance, invalid cookie rejection, record-by-record reads, EOF on invalid record or table bound, small-buffer `-EINVAL`, PSP address failure handling, and userspace decoding of firmware ID/version/source fields.
