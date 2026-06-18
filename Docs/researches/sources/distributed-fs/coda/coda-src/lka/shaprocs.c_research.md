# sources/distributed-fs/coda/coda-src/lka/shaprocs.c

Purpose: SHA helper implementation used by LKA creation, testing, and runtime verification. It converts SHA bytes to hex, copies files while hashing, and detects all-zero SHA values.

APIs and flow: `CopyAndComputeViceSHA` initializes SHA-1, reads 4096-byte chunks, updates the digest, optionally writes chunks to an output fd, and yields every 200 chunks through `LWP_DispatchProcess`. `ViceSHAtoHex` formats a 40-character hex digest if the destination is large enough. `IsZeroSHA` scans for nonzero bytes.

Dependencies and risks: depends on `coda_hash` SHA wrappers and LWP. Partial writes are treated as errors but not retried; read/write interruption handling is minimal. SHA-1 is the persistent lookup identity. Tests are indirect through `mklka` and `testlka`.
