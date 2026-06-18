# sources/distributed-fs/coda/coda-src/vol/vollocate.h

Purpose: declares the volume key resolution API.

Important API: `VolumeId VOL_Locate(char *volkey)` resolves names or ids through VRDB/VLDB logic. It includes `vcrcommon.h` for volume id/common replication types.

Control flow/state: no state in the header; the implementation consults global VRDB/VLDB/server state.

Dependencies/integration: used by volume utilities that accept flexible volume names or ids. Risks are a mutable `char *` signature for a read-only key and lack of error-code distinction because zero/missing can be ambiguous. Test signals: compile utility consumers and test all lookup fallbacks.
