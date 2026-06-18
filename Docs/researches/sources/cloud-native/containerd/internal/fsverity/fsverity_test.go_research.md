# sources/cloud-native/containerd/internal/fsverity/fsverity_test.go

## Purpose
Tests enabling fs-verity on supported Linux/ext4 systems and contains helpers to inspect ext4 feature flags.

## Important APIs, Types, And Functions
`TestEnable` creates a temp file, resolves its backing device, checks ext4 verity support with `ext4IsVerity`, calls `Enable`, and checks `IsEnabled`. Helpers parse `/proc/self/mountinfo` and read ext4 superblock feature bits.

## Control Flow
The test requires root, skips non-ext4 or unsupported devices, creates/removes a temp file, and compares runtime support with expected filesystem support.

## State And Persistence
Temporarily creates an fs-verity-enabled file and reads host mount/device metadata.

## Dependencies And Integration Points
Uses `testutil.RequiresRoot`, `unix` major/minor helpers, binary decoding, and OS mountinfo.

## Risks
Highly environment-dependent. It assumes ext4 and direct device readability, and it mutates a file into immutable fs-verity state before removal.

## Test Signals
Good integration signal on properly configured ext4 hosts; otherwise mostly skip behavior.
