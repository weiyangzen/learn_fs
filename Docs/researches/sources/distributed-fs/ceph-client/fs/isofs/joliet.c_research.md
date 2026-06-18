## sources/distributed-fs/ceph-client/fs/isofs/joliet.c

Purpose: converts Joliet UCS-2 big-endian filenames into Linux-visible names.

Important APIs: `get_joliet_filename` chooses UTF-8 conversion via `utf16s_to_utf8s` when no NLS table is loaded, or `uni16_to_x8` through `nls->uni2char` otherwise. It strips trailing `;1` version suffixes and trailing periods for Windows-compatible behavior.

Control flow: `uni16_to_x8` walks 16-bit characters until NUL or the input character count ends, emits converted bytes or `?` for unmappable characters, and NUL-terminates the output. `get_joliet_filename` passes half the ISO directory name length because Joliet names are 16-bit units.

State and persistence: no persistent state. It reads `s_nls_iocharset` from the mounted superblock and writes a temporary output name buffer used by lookup/readdir.

Dependencies and integration points: depends on `CONFIG_JOLIET`, NLS, UTF-16 helpers, and ISOFS directory/name lookup code.

Risks and test signals: risks are output buffer sizing, odd-length names, unmappable characters, and suffix stripping after multibyte conversion. Test with Unicode names, default UTF-8, explicit legacy iocharset, trailing dot/version suffix, and names containing unmappable characters.
