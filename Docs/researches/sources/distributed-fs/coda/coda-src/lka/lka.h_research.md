# sources/distributed-fs/coda/coda-src/lka/lka.h

Purpose: public interface for the lookaside subsystem. It exposes SHA helper routines and the two Venus-facing operations: fill a container from registered databases and parse/execute LKA control commands.

Important APIs: `ViceSHAtoHex`, `CopyAndComputeViceSHA`, `ComputeViceSHA`, and `IsZeroSHA` operate on `SHA_DIGEST_LENGTH` byte arrays. `LookAsideAndFillContainer` performs lookup/copy/verification. `LKParseAndExecute` implements command-string control.

Dependencies and risks: includes `coda_hash.h` for SHA definitions and expects `shaprocs.c`/`lka.c` implementations. The header makes SHA-1 a visible contract; any digest migration must change database format, helper lengths, and callers. Test signals are compile-time API compatibility plus `mklka`/`testlka`.
