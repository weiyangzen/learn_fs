# sources/distributed-fs/lizardfs/src/tools/quota_rep.cc

Purpose: Implements `lizardfs repquota`, reporting user, group, all, or per-directory quota usage and limits.

Important APIs/types/functions: `quota_rep_run`; static `quota_rep`; `quota_print_rep`; `quota_print_entry`; `quota_putc_plus_or_minus`; `cltoma::fuseGetQuota`; `matocl::fuseGetQuota`; `QuotaEntry`; `QuotaDatabase::Limits`.

Control flow: Parses mutually exclusive selector modes (`-u`/`-g`, `-a`, or `-d`) and formatting flags, opens a master connection, verifies root path for user/group/all quota unless directory quota is requested, builds requested `QuotaOwner`s, sends a typed get-quota request, handles status-vs-response packet versions, sorts entries, groups limits by owner, and prints a quota table.

State and persistence: Read-only. It materializes quota entries into local tables for printing.

Dependencies and integration: Uses `ServerConnection`, quota protocol structs, master quota database table shape, and common formatting helpers. It is the reporting counterpart to `quota_set.cc`.

Risks and test signals: Enum values are cast to table indices, so protocol enum ordering matters. Usage validation uses XOR logic to enforce exactly one selector family. No direct tests in this subset.
