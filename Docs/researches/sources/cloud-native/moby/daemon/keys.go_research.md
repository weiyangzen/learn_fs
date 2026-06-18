# sources/cloud-native/moby/daemon/keys.go

## Purpose
Raises Linux root keyring limits for the daemon when the kernel configuration is below Docker's expected threshold.

## Important APIs, Types, And Functions
Constants point to `/proc/sys/kernel/keys/root_maxkeys` and `root_maxbytes`, with `rootKeyLimit` 1,000,000 and byte multiplier 25. `modifyRootKeyLimit` reads the current key limit and calls `setRootKeyLimit` only when it is lower. `setRootKeyLimit` writes both maxkeys and maxbytes. `readRootKeyLimit` reads and trims the proc file.

## Control Flow
Startup code can call `modifyRootKeyLimit`; if the existing setting is already high enough, no writes occur. When writing, maxkeys is updated first, then maxbytes.

## State And Persistence
Mutates kernel sysctl state via procfs. These settings affect the running system and may persist depending on host sysctl configuration outside this code.

## Dependencies And Integration Points
Linux-only daemon startup support for overlay/network/security features that can consume kernel keys.

## Risks And Test Signals
Requires permission to write procfs. If maxkeys write succeeds and maxbytes write fails, the system is left partially updated. No tests are included in this subset.
