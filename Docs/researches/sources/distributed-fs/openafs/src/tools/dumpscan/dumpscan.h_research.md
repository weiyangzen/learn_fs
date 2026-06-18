# sources/distributed-fs/openafs/src/tools/dumpscan/dumpscan.h

Purpose: public API for the dumpscan library, including data models, parser callbacks, flags, path hash types, and exported functions.

Important types: `backup_system_header`, `afs_dump_header`, `afs_vol_header`, `afs_vnode`, and `afs_dir_entry` carry parsed dump data with field masks. `tagged_field` and `tag_parse_info` drive generic tag parsing and recovery flags. `dump_parser` is the primary integration contract, containing callbacks for backup headers, dump/volume headers, vnode categories, data, errors, directory entries, plus `DSFLAG_SEEK`, `DSPRINT_*`, and `DSFIX_*` flags. `path_hashinfo` and `vhash_ent` support path construction/following.

Integration points: command-line tools configure `dump_parser` and call `ParseDumpFile`; repair and extraction callbacks use offsets and field masks; writers use the same model for output.

Risks/test signals: callbacks receive stack-owned records and must copy data they retain. Many operations require seekable `XFILE`s but this is represented by a flag rather than enforced by the type system. Test signals include compile-time API consistency and successful parse/path/extract/repair workflows.
