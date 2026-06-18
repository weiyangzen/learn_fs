<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/randomid.go -->
# sources/cloud-native/containers-storage/drivers/overlay/randomid.go

## Purpose
`randomid.go` generates compact random link identifiers for overlay layer symlinks under `home/l`.

## Important APIs, Types, And Functions
`generateID(l int)` reads enough random bytes from `crypto/rand`, base32-encodes them, and returns the requested prefix length. `retryOnError` unwraps `*os.PathError` and treats `unix.EPERM` as retryable entropy exhaustion.

## Control Flow
The generator computes byte count as `(l*5+7)/8`, repeatedly reads from `rand.Reader`, sleeps with a 10 ms incremental backoff on retryable errors, and panics on non-retryable or exhausted retry failures. Successful bytes are base32 encoded.

## State And Persistence
The function has no durable state. Its output becomes persistent when `overlay.go` writes it to each layer `link` file and creates a symlink in `home/l`.

## Dependencies And Integration Points
Overlay layer creation uses `generateID(idLength)` to keep lowerdir mount arguments short while avoiding collisions. Dependencies are standard crypto/base32/time/os/syscall plus logrus and unix constants.

## Risks And Test Signals
The function panics instead of returning an error if randomness fails, making it a process-level failure path. It does not check collision itself; callers depend on symlink creation failure to catch collisions. There is no file-local test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/randomid.go -->
