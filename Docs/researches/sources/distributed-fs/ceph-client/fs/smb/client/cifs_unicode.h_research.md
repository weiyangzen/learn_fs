<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.h

Purpose: declares CIFS Unicode/NLS conversion APIs and constants for SFM/SFU reserved-character remapping.

Important APIs and symbols: defines SFM private-use codepoints for double quote, asterisk, question mark, colon, greater-than, less-than, pipe, slash, trailing space, and trailing period. Remap modes are `NO_MAP_UNI_RSVD`, `SFM_MAP_UNI_RSVD`, and `SFU_MAP_UNI_RSVD`. Declares conversion functions between UTF-16LE and local strings, duplication helpers, `cifs_toupper()`, and inline `cifs_remap()`.

Control flow: `cifs_remap()` inspects `cifs_sb_flags()` and gives priority to `CIFS_MOUNT_MAP_SFM_CHR` over `CIFS_MOUNT_MAP_SPECIAL_CHR`, selecting the remap mode passed into conversion functions.

State and persistence: no state in the header. Constants are part of cross-platform filename compatibility behavior and should be treated as stable.

Dependencies and integration: includes byteorder, types, NLS, UCS-2 utilities, CIFS globals, and mount flags through `cifs_sb_info`.

Risks: remap mode priority affects whether filenames round-trip with Mac-style or SFU-style encodings. Adding new reserved characters must align with server behavior and readdir/open symmetry.

Test signals: compile all conversion users, verify mount flag to remap mode mapping, round-trip filenames under each remap mode, and confirm no remap mode leaves reserved private-use values untouched except through normal NLS conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.h -->
