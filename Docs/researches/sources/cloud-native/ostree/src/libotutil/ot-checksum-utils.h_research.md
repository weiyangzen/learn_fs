# sources/cloud-native/ostree/src/libotutil/ot-checksum-utils.h

## Purpose
Declares checksum utility APIs and the ABI-sized `OtChecksum` storage wrapper.

## Important APIs, Types, And Functions
Defines `_OSTREE_SHA256_DIGEST_LEN`, `_OSTREE_SHA256_STRING_LEN`, `OtChecksum`, cleanup support, `ot_bin2hex`, `ot_csum_from_gchecksum`, checksum init/update/digest/hex/clear APIs, `ot_checksum_update_bytes`, GIO write/splice checksum helpers, `ot_checksum_file_at`, and `ot_checksum_bytes`.

## Control Flow
No runtime flow. The inline `ot_checksum_update_bytes` extracts data from `GBytes` and delegates to `ot_checksum_update`.

## State And Persistence Behavior
`OtChecksum` is an opaque fixed-size struct large enough for the backend-specific implementation. Size assertions in the implementation enforce storage compatibility.

## Dependencies And Integration Points
Depends on `libglnx.h`, GLib/GIO stream types, and OSTree SHA256 constants when available. It is widely shared by libostree and otcore code.

## Risks
The fixed storage size must remain large enough for `OtRealChecksum`; backend changes can silently require size updates. The header exposes only SHA256-sized constants despite taking `GChecksumType` in one API.

## Test Signals
Compile checks across crypto feature combinations, static assertion coverage, and known-vector tests through all declared APIs are relevant.
