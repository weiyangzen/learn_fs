# sources/distributed-fs/openafs/src/butm/butm_prototypes.h

Purpose: private/provided prototypes for the file tape module implementation. It exposes helpers used by butm tests and callers that need direct instantiation of the file-backed tape module.

Important APIs: declares `incSize`, `SeekFile`, `butm_file_Instantiate`, and `NextFile`. `butm_file_Instantiate` is the key factory that fills a `struct butm_tapeInfo` operation table from a `struct tapeConfig`.

Control flow and state: no executable logic. The declarations imply external code can manipulate tape position/accounting helpers, so the implementation cannot treat those as fully private.

Dependencies and integration: requires prior visibility of `struct butm_tapeInfo`, `struct tapeConfig`, and `afs_uint32`, normally through `<afs/butm.h>` and OpenAFS standard headers.

Risks and tests: exposing low-level helpers increases coupling to `file_tm.c` internals. Build coverage comes from the butm Makefile installing this header and compiling `butm_test`/`test_ftm`.
