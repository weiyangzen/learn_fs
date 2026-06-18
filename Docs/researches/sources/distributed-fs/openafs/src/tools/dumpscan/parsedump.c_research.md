# sources/distributed-fs/openafs/src/tools/dumpscan/parsedump.c

Purpose: top-level parser for AFS volume dump streams and public wrappers for parsing a full dump, just a dump header, just a volume header, or one vnode.

Important APIs/functions: `top_fields` maps top-level tags to `parse_dumphdr`, `parse_volhdr`, `parse_vnode`, `parse_dumpend`, and `try_backuphdr`. `parse_dumphdr` validates begin magic/version, parses attributes with `dumphdr_fields`, invokes `cb_dumphdr`, and frees kept strings. `parse_dumptimes` reads the two-entry from/to array. `parse_dumpend` validates trailer magic and returns `DSERR_DONE`. Public `ParseDumpFile`, `ParseDumpHeader`, `ParseVolumeHeader`, and `ParseVNode` set up `tag_parse_info` via `prep_pi` and normalize returns through `handle_return`.

State/dependencies: parser state is callback-driven and transient; `dump_parser` may record `vol_uniquifier` later via volume parsing. Dependencies are `dumpfmt.h`, `internal.h`, `stagehdr.h`, and primitive/tag parsing.

Risks/test signals: unknown tags stop current object parsing by returning zero for higher-level handling, so stream position discipline is critical. Magic/version checks are strong early corruption signals.
