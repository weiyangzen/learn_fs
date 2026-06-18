## sources/distributed-fs/coda/coda-src/volutil/tar-FromRedHatCD.h

Purpose: `tar-FromRedHatCD.h` is a bundled GNU tar archive-format definition used by `codadump2tar.cc` to construct tar headers without relying on the system `<tar.h>`.

Important APIs/types/functions: it defines `struct posix_header`, GNU sparse/extra/oldgnu header structs, tar typeflag constants (`REGTYPE`, `LNKTYPE`, `SYMTYPE`, `DIRTYPE`, etc.), permission bit constants, `BLOCKSIZE`, GNU extension type constants, `enum archive_format`, and `union block`.

Control flow: no executable flow; it provides layout and constants. `TarRecd` writes into `union block.header`, fills POSIX fields, computes checksums over `BLOCKSIZE`, and writes the raw block.

State and persistence behavior: none directly. Its struct layout defines the persistent tar bytes emitted by the converter.

Dependencies/integration points: included only by `codadump2tar.cc` in this subset. The comments describe GNU tar historical compatibility; `codadump2tar` uses the POSIX header portion and basic type constants, not sparse extensions.

Risks: this is a copied historical header under GPL terms and may differ from modern tar semantics. Fixed arrays enforce classic ustar limits: 100-byte name, 155-byte prefix, 100-byte linkname, and octal size fields. The converter does not implement GNU long-name records, so paths beyond these limits are truncated before using this layout.

Test signals: verify generated headers with GNU tar and bsdtar, including directory, file, symlink, and hard-link records; validate checksum calculation and zero trailer. Include boundary names/prefixes and sizes near octal field limits.
