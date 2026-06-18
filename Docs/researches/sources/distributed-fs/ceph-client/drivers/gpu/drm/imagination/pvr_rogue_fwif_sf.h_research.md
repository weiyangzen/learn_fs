# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_sf.h

Purpose: This header is the firmware trace string-format catalog. It maps firmware string-format IDs to host-readable format strings and defines the ID encoding used in firmware trace buffers. It explicitly warns that group/order compatibility must not be broken.

Important APIs/types/functions: `enum rogue_fw_log_sfgroups` defines trace groups: null, main, cleanup, context switch, PM, RTD, SPM, MTS, BIF, misc, power, HWR, HWP, RPM, DMA, and debug. `PVR_SF_STRING_MAX_SIZE` bounds firmware-side strings. `rogue_fw_stid_fmt` and `rogue_km_stid_fmt` describe ID/string pairs. ID macros include `ROGUE_FW_LOG_IDMARKER`, `ROGUE_FW_LOG_CREATESFID(id, group, params)`, `ROGUE_FW_LOG_IDMASK`, `ROGUE_FW_LOG_VALIDID`, `ROGUE_FW_SF_GID`, and `ROGUE_FW_SF_PARAMNUM`. `stid_fmts[]` is the static kernel decode table, with hundreds of entries covering workload kicks, UFO checks/updates, HWR, power, cleanup, context switching, PM/SPM/RTD, HWPerf, DMA, and debug messages. Boundary constants include `ROGUE_FW_SF_FIRST`, `ROGUE_FW_SF_MAIN_ASSERT_FAILED`, and `ROGUE_FW_SF_LAST`.

Control flow: No driver control flow, but trace decoding flow is fixed: firmware writes an encoded SFID and parameters; host validates the ID marker, extracts group and parameter count, looks up the matching `stid_fmts` entry, and formats the trace message.

State and persistence behavior: The static table is read-only kernel data. Its ordering and numeric IDs are persistent firmware trace ABI; historical firmware logs depend on entries retaining their IDs and format parameter counts.

Dependencies and integration points: Uses `u32` types from the including environment. It integrates with `pvr_rogue_fwif.h` trace buffers, debugfs/log decoding, firmware assert reporting, HWR diagnostics, and support tooling that groups logs by the encoded group ID.

Risks: Reordering, deleting, or changing parameter counts breaks decoding of both live and archived firmware traces. Format-string/type mismatches can corrupt log output. The ID uses only four bits for parameter count and group, so new groups/large parameter counts must fit the encoding.

Test signals: Build coverage, trace decoding unit tests for valid/invalid IDs, firmware assert log parsing, HWR trace dumps, and comparison of known firmware trace buffers against expected strings.
