# sources/distributed-fs/openafs/src/tools/dumpscan/repair.c

Purpose: callback set for generating a repaired AFS dump from a parsed possibly incomplete/corrupt input dump.

Important APIs/functions: global `repair_output` is the output `XFILE`. `repair_dumphdr_cb` requires volume ID and synthesizes volume name/from/to times as needed before `DumpDumpHeader`. `repair_volhdr_cb` fills missing or bogus volume fields such as version, name, service flags, uniquifier, type, parent, quota, disk usage, file count, and dates before `DumpVolumeHeader`. `repair_vnode_cb` infers missing vnode type/metadata, creates default ACLs for directories, writes vnode attributes, copies existing data, or synthesizes an empty/default directory page.

State/persistence: writes a new dump to `repair_output`; uses `repair_verbose` for diagnostics. Dependencies include `dump.c`, `dumpfmt.h`, `afs/acl.h`, `afs/dir.h`, and vnode offsets from parsing.

Risks/test signals: generated defaults are lossy and may create semantically incorrect but structurally parseable dumps. The default ACL branch appears to set total differently depending on owner in a way worth review. Test signals are reparsed output dumps and successful restore/salvage behavior.
