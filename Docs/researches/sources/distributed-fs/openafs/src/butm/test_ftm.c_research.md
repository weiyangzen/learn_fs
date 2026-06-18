# sources/distributed-fs/openafs/src/butm/test_ftm.c

Purpose: end-to-end tape module data integrity test. It writes one or more regular files to a configured tape/file target using `butm`, writes EOD, remounts, reads the data back, and compares labels and file contents.

Important APIs and types: `GetDeviceInfo` parses test configuration into `struct tapeConfig`. `PerformDumpTest` performs the write/readback workflow using `butm_file_Instantiate`, `butm_Mount`, `butm_Create`, `butm_WriteFileBegin/Data/End`, `butm_WriteEOT`, `butm_ReadLabel`, `butm_ReadFileBegin/Data/End`, and `butm_SeekEODump` for append testing. `TestInfo` carries tape name, config, file list, and append flag.

Control flow and state: `main` parses `-configuration`, `-tapename`, and file arguments, filters readable regular files, initializes LWP/IOMGR, runs a normal dump test thread, and runs an appended test when target is a real tape. `PerformDumpTest` writes metadata labels, streams source files block by block, then validates label fields and content bytes on readback.

Dependencies and integration: uses LWP process creation/signaling, com_err, USD-backed `file_tm`, and filesystem input files. It reads a config format of capacity, device name, port, and `isafile`.

Risks and tests: the content comparison only checks one advancing byte per block (`tbuffer[tprogress++]`), not every byte, weakening integrity coverage. It uses global `bufferBlock` and `isafile`, and can touch real tape devices. Still, it is the strongest local signal for label, filemark, EOD, and append integration.
