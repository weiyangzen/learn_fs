# sources/distributed-fs/openafs/src/butc/tdump.c

Purpose: small diagnostic utility for inspecting raw backup tape/file blocks. It opens the path supplied as `argv[1]`, repeatedly reads a fixed block size of `4096 + 24`, and prints the first sixteen 32-bit words in hexadecimal for each block, emitting `***EOF***` on zero-byte reads.

Important APIs: `glong` copies an `afs_int32` from a byte buffer at a 32-bit index; `main` performs the open/read/print loop. On AIX it installs full-core signal behavior for `SIGABRT` and `SIGSEGV`.

Control flow and state: there is no persistent state beyond the input file descriptor and local read buffer. The tool exits on open failure, short read, or negative read. It does not parse the `butm` structures semantically; it only exposes raw words useful when debugging the tape module format.

Dependencies and integration: uses roken/OpenAFS configuration headers and `AFS_component_version_number.c`. It is a debugging companion for butc/butm tape formats and assumes a legacy backup tape block size distinct from `BUTM_BLOCKSIZE`.

Risks and tests: there is no argument count validation before `argv[1]`, so invoking without an argument dereferences invalid memory. The fixed block size may not match all current tape-module writes. Test signal is manual use against known tape images.
