# sources/distributed-fs/openafs/src/tools/dumpscan/parsevol.c

Purpose: parses AFS volume header records from tagged dump data into `afs_vol_header`.

Important APIs/functions: `parse_volhdr` initializes the header, records offset, calls `ParseTaggedData` with `volhdr_fields`, invokes `cb_volhdr`, stores `voluniq` into `dump_parser.vol_uniquifier`, and frees kept strings. `store_volhdr` handles scalar, flag, time, and string fields while setting field masks. `parse_weekuse` reads and validates a seven-element usage array.

State/dependencies: persistent parser side effect is `p->vol_uniquifier`. The header and strings are transient; callbacks must copy what they keep. Dependencies are `dumpfmt.h`, `dumpscan_errs.h`, primitive readers, and time formatting.

Risks/test signals: weekuse count mismatch is fatal format error. String ownership depends on `DSERR_KEEP`, and volume header completeness is not enforced here; repair callbacks fill missing fields later. Printing uses raw integer/time formatting and is mostly diagnostic.
