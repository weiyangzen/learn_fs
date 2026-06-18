# sources/cloud-native/moby/daemon/graphdriver/overlayutils/randomid.go

Purpose: random short-link ID generation for overlay-style graphdrivers.

Important APIs and control flow: `GenerateID` computes the needed random byte count for the requested base32 length, reads from `crypto/rand.Reader`, retries partial/retryable failures with incremental 10 ms backoff up to nine retries, logs retryable errors, base32-encodes the bytes, and truncates to the requested length. `retryOnError` unwraps `os.PathError` and treats `EPERM` as retryable for entropy-pool-related conditions.

State, dependencies, and risks: no persistent state; temporary state is the random byte buffer and retry counters. Dependencies are cryptographic randomness, base32 encoding, logging, and Unix errno. On unrecoverable random-source failure it panics, which is acceptable because unique layer link IDs are required. There is no collision check here; callers rely on random entropy and symlink creation failure if a collision occurs. Test coverage is indirect through overlay2/fuse-overlayfs layer creation.
