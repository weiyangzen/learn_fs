# sources/distributed-fs/coda/coda-src/vol/vrdb.h

Purpose: declares the replicated volume database types, file paths, and translation APIs.

Important types/APIs: `vrtab` extends `ohashtab` and owns a secondary `namehtb`; it can add/remove/find/clear/print/dump `vrent` entries. `vrent` stores name key, replicated volume id, name hash link, server count, per-server replica volume numbers, and helpers for host/index lookup, check VV generation, `VolumeInfo` population, byte-order conversion, printing, and dumping. Public functions are `CheckVRDB`, `DumpVRDB`, `XlateVid`, and `ReverseXlateVid`.

Control flow/state: `VRDB_PATH`, `VRDB_TEMP`, and `VRLIST_PATH` locate database inputs/outputs. `VRTABHASHSIZE` fixes hash-table sizing.

Dependencies/integration: includes `vcrcommon`, `vice`, `ohash`, inconsistency utilities, `vice_file`, and deprecation warnings. Risks include unusual `public :` formatting, public data fields, raw char key buffer, and unsupported assignment operator that aborts. Test signals: compile users, reload/dump, field size compatibility with `testvrdb`, and single-homing warnings for host helpers.
