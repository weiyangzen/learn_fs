# sources/distributed-fs/lizardfs/src/tools/get_eattr.cc

Purpose: Implements `lizardfs geteattr`, reporting extra attributes on objects either directly or recursively.

Important APIs/types/functions: `get_eattr_run`; static `get_eattr`; `CLTOMA_FUSE_GETEATTR`; `MATOCL_FUSE_GETEATTR`; modes `GMODE_NORMAL` and `GMODE_RECURSIVE`; `eattrtab` and `eattrdesc`.

Control flow: Parses recursive and number-format options, sends a legacy get-extra-attributes request with inode and mode, validates response length, then either prints a comma-separated attribute set for a single object or aggregates recursive file/directory counts for each attribute bit.

State and persistence: Read-only master query. Uses global formatting mode and global eattr name tables.

Dependencies and integration: Uses common tool helpers, legacy datapack protocol, and master-defined extra attribute constants. Integrates with `set_eattr.cc` as the read side of the eattr tool pair.

Risks and test signals: Response length and count validation is strict but manual. Unknown attribute bits are printed as unknown in recursive mode. No direct tests in this subset.
