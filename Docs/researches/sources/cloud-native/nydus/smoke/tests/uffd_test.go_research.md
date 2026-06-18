# sources/cloud-native/nydus/smoke/tests/uffd_test.go

## Purpose
This suite validates Nydus `nydusd uffd` block-device mode lifecycle, restart behavior, error handling for missing bootstraps, and data correctness in zerocopy and copy policies.

## Important APIs, Types, And Functions
`UffdTestSuite` stores `T`. `buildLayer` creates a RAFS v6 thin layer and bootstrap without special files. `TestUffdDaemonLifecycle` starts `nydusd uffd`, waits for `RUNNING`, and checks socket creation. `TestUffdDaemonRestart` starts, shuts down, removes the leftover socket, and starts again on the same path. `TestUffdDaemonMissingBootstrap` expects invalid bootstrap startup not to reach `RUNNING`. `TestUffdZerocopyDataVerification` and `TestUffdCopyDataVerification` export a reference disk image when possible, start UFFD daemon, connect `tool.UffdClient`, handshake with the selected policy, verify EROFS magic, and call `verifyDataAtOffsets`. `verifyDataAtOffsets` reads aligned offsets across the device and compares to exported disk bytes when available.

## Control Flow
Each case prepares a temp context and bootstrap, starts UFFD daemon through `tool.NewNydusdUffd`, waits or expects failure, then optionally uses `UffdClient` to trigger page faults by reading mapped memory. Data verification samples start, interior, and tail offsets.

## State And Persistence
The workdir contains blobs, bootstrap, UFFD socket, API socket, and optional `disk.raw` export. UFFD client state includes mmap and userfaultfd resources cleaned by `Close`.

## Dependencies And Integration Points
This integrates `texture.MakeThinLowerLayer`, `snapshotter-converter`, `tool.NydusdUffd`, `tool.UffdClient`, kernel userfaultfd, and `nydus-image export --block`.

## Risks
The tests are Linux/kernel-feature dependent and may require userfaultfd permissions. Export failure downgrades verification to EROFS magic and accessible reads, reducing coverage. Missing-bootstrap test waits for the full `WaitStatus` timeout before passing unless the API fails earlier.

## Test Signals
Signals include daemon state, socket existence, restart on reused path after manual unlink, expected failure for invalid bootstrap, successful UFFD handshakes, EROFS magic match, and sampled data equality with exported raw disk when available.
