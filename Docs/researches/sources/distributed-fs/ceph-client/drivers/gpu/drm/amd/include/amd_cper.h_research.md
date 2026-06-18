# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_cper.h

## Purpose
This header defines AMDGPU Common Platform Error Record structures, GUIDs, revisions, severities, and register-dump layouts used for GPU RAS crash, boot, and nonstandard error reporting.

## Important APIs, Types, And Constants
Constants include `CPER_HDR_REV_1`, section revision values, `CPER_MAX_OAM_COUNT`, context types `CPER_CTX_TYPE_CRASH` and `CPER_CTX_TYPE_BOOT`, and `CPER_CREATOR_ID_AMDGPU`. GUID macros identify notification types (`CPER_NOTIFY_MCE`, `CPER_NOTIFY_CMC`, `BOOT_TYPE`) and section types (`AMD_CRASHDUMP`, `AMD_GPU_NONSTANDARD_ERROR`, `PROC_ERR_SECTION_TYPE`).

`enum cper_error_severity` represents corrected, nonfatal uncorrected, fatal, and unused severities. `enum cper_aca_reg` names the low/high ACA register slots with `CPER_ACA_REG_COUNT` set to 32.

Packed structures define the binary record format: `cper_timestamp`, `cper_hdr`, `cper_sec_desc`, `cper_sec_nonstd_err_hdr`, `cper_sec_nonstd_err_info`, `cper_sec_nonstd_err_ctx`, `cper_sec_nonstd_err`, `cper_sec_crashdump_hdr`, `cper_sec_crashdump_reg_data`, `cper_sec_crashdump_body_fatal`, `cper_sec_crashdump_body_boot`, `cper_sec_crashdump_fatal`, and `cper_sec_crashdump_boot`.

## Control Flow
There are no functions. RAS and CPER producer/consumer code includes this header, fills a `cper_hdr`, appends section descriptors, and serializes one of the section bodies depending on whether the event is runtime nonstandard error, fatal crashdump, or boot/OAM message data.

## State And Persistence
The structures describe persisted firmware/OS error records. The header itself has no mutable state, but the records it formats may be stored in RAS buffers, exposed via debugfs/sysfs or command paths, and retained as platform error evidence.

## Dependencies And Integration Points
The only direct include is `<linux/uuid.h>` for `guid_t` and `GUID_INIT`. In this source tree, `amdgpu/amdgpu_cper.h` includes this file, and RAS command paths reference CPER snapshot and record retrieval. The data layout must also align with platform CPER consumers outside AMDGPU.

## Risks
The header uses `#pragma pack(push, 1)` around the binary layouts. Any accidental field change affects externally consumed record offsets. Bitfields inside fixed-width integers are convenient for driver code but should be treated cautiously across compiler and endian assumptions; serialization tests should inspect masks, not just named bitfields.

There is a nearby RAS-specific CPER header in `ras/rascore/ras_cper.h` with similar concepts and different names/counts. Keeping both definitions coherent is important to avoid converting or interpreting records with the wrong layout.

## Test Signals
Compile coverage through `amdgpu_cper.h` is the first signal. Stronger validation should build representative fatal, boot, and nonstandard records and assert exact sizes, offsets, GUID bytes, section lengths, and severity values. RAS command tests for CPER snapshot and CPER record retrieval are integration signals.
