# sources/distributed-fs/openafs/src/butm/butm_test.c

Purpose: simple behavioral test harness for `file_tm.c` error handling and sequencing. It instantiates a `butm_tapeInfo`, initializes LWP/IOMGR, and checks expected return codes for invalid and basic tape operations.

Important APIs: uses `butm_file_Instantiate` and direct `tapeInfo.ops.*` calls for mount, dismount, read/write file begin/end/data. Macros `PASS` and `PASSq` compare returned `code` against expected values and print results.

Control flow and state: first verifies operations fail with `BUTM_NOMOUNT` before mounting, checks bad file-end sequencing, writes then reads an empty file stream, then tests bad `writeFileData`/`readFileData` arguments and call order. Global `isafile` and `debugLevel` configure file tape behavior.

Dependencies and integration: depends on LWP, com_err, `butm.h`, and `butm_prototypes.h`; initializes the BUTM error table for readable diagnostics. The hard-coded device is `/dev/rmt0`, so the test targets real tape defaults unless the environment changes globals elsewhere.

Risks and tests: `PASS` prints failures but does not force process failure, so automated consumers may see exit 0 despite failed expectations. The calls to `writeFileData` pass argument positions that reflect the operation signature and can be easy to misread. It is useful smoke coverage for state-machine errors, not data integrity.
