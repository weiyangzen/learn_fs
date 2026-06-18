<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.c

Purpose: performs CIFS/SMB pathname and string conversion between wire-format UTF-16LE and local NLS encodings, including SFU and SFM reserved-character remapping.

Important APIs: external functions include `cifs_from_utf16()`, `cifs_utf16_bytes()`, `cifs_strtoUTF16()`, `cifs_strndup_from_utf16()`, `cifsConvertToUTF16()`, and `cifs_strndup_to_utf16()`. Internal helpers include `convert_sfu_char()`, `convert_sfm_char()`, `cifs_mapchar()`, `convert_to_sfu_char()`, `convert_to_sfm_char()`, and `cifs_local_to_utf16_bytes()`.

Control flow: inbound conversion walks UTF-16 words with unaligned little-endian loads, optionally maps SFU/SFM private-use codepoints back to reserved local characters, uses `uni2char()`, and falls back to UTF-8 surrogate/variation handling or `?`. Outbound conversion either delegates to `cifs_strtoUTF16()` for no remap, or scans source bytes, applies SFU/SFM mappings for reserved characters and trailing spaces/periods, converts through NLS `char2uni()`, and handles UTF-8 surrogate/IVS sequences with `utf8s_to_utf16s()`.

State and persistence: no global state. Behavior is driven by the local `nls_table`, source buffers, and remap mode selected from mount flags.

Dependencies and integration: depends on NLS tables, UCS-2/UTF-16 utility helpers, mount flags from `cifs_fs_sb.h`, SMB path-building code, and filename semantics for Windows, Services for Unix, and Services for Mac compatibility.

Risks: path separators cannot be remapped until path-building code changes, explicitly leaving slash/backslash limitations. Buffer sizing is caller-sensitive; `cifsConvertToUTF16()` assumes target capacity. Surrogate-pair and IVS handling is specialized for UTF-8 and can fall back to `?`. SFM trailing space/period handling has special cases for `.` and `..` symlink targets.

Test signals: UTF-8 and non-UTF-8 NLS conversions, malformed byte sequences, surrogate pairs, IVS sequences, SFU and SFM reserved character round trips, trailing space and period components, `.` and `..` preservation, max-length truncation, unaligned UTF-16 source buffers, and mount flag selection via `cifs_remap()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.c -->
