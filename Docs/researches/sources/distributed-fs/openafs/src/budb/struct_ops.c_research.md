# sources/distributed-fs/openafs/src/budb/struct_ops.c

## Purpose
`struct_ops.c` centralizes BUDB structure diagnostics and conversions. It prints internal and RPC-facing backup database records, converts selected structures between network and host byte order, and copies internal database records into public `budb_*Entry` forms returned to clients.

## Important APIs, Types, And Functions
Print helpers cover `DbHeader`, `dump`, `budb_dumpEntry`, `memoryHashTable`, `budb_principal`, `structDumpHeader`, `tape`, `budb_tapeEntry`, `budb_tapeSet`, `budb_volumeEntry`, `volFragment`, and `volInfo`. Host/network conversion helpers include `volFragment_ntoh()`, `volInfo_ntoh()`, `tape_ntoh()`, `dump_ntoh()`, `DbHeader_ntoh()`, `dumpEntry_ntoh()`, `principal_hton()`, `principal_ntoh()`, `structDumpHeader_hton()`, `structDumpHeader_ntoh()`, `tapeEntry_ntoh()`, `tapeSet_hton()`, `tapeSet_ntoh()`, `textBlock_hton()`, `textBlock_ntoh()`, `textLock_hton()`, `textLock_ntoh()`, and `volumeEntry_ntoh()`. Public-copy helpers are `copy_ktcPrincipal_to_budbPrincipal()`, `dumpToBudbDump()`, `tapeToBudbTape()`, `volsToBudbVol()`, and `default_tapeset()`.

## Control Flow
The print routines are direct field renderers with light interpretation of BUDB flag bits. The byte-order routines perform field-by-field numeric conversion while string fields are copied as-is. Internal-to-public conversion routines assume host-order internal records and copy the subset of fields required by BUDB RPC/client structures. `default_tapeset()` zeroes a `budb_tapeSet`, creates the default `dumpname.%d` format, and initializes sequence fields.

## State And Persistence
The file has no durable state and no own global mutable state. Its effect is by copying, printing, and initializing caller-provided structures. Persistence relevance is indirect: these routines must match the database block layout and RPC structure contracts so dumps, restores, and admin displays interpret persisted BUDB records correctly.

## Dependencies And Integration Points
It depends on BUDB database layout headers (`database.h`, `budb.h`, `budb_internal.h`) and OpenAFS/Rx byte-order utilities. It is used by BUDB diagnostics, dump/restore code, and RPC conversion paths that bridge internal Ubik records to client-facing `budb_*` entries.

## Risks And Test Signals
The dominant risk is fixed-size string copying with `strcpy()`/`strncpy()` into legacy structure fields; callers must ensure source records are valid and bounded. Another risk is schema drift: adding fields to BUDB structures without updating these conversion routines silently loses or misreports data. Test signals should include round-trip byte-order tests on representative structures, default tape-set formatting, flag rendering for dump/tape/volume status combinations, and conversion of internal dump/tape/volume records into public entries.
