# sources/cloud-native/moby/daemon/internal/usergroup/add_linux_test.go

## Purpose
Integration-tests Linux user creation, subordinate ID mapping, lookup, and mapped filesystem access for user namespace support.

## Important APIs, Types, And Functions
`TestNewIDMappings` calls `AddNamespaceRangesUser`, `LoadIdentityMapping`, `RootPair`, `MkdirAllAndChown`, and runs `ls` with `syscall.Credential`. `TestLookupUserAndGroup` verifies name and numeric lookup parity. `delUser` removes the temporary user with `userdel`.

## Control Flow
Tests skip unless running as root. Each creates `tempuser`, defers deletion, then checks either identity mapping and directory access or lookup by name and id.

## State And Persistence
These tests mutate host user/group databases and subordinate ID files. Cleanup uses `userdel` but failures may leave state behind.

## Dependencies And Integration Points
Requires root, system account tools, subordinate ID support, and `moby/sys/user`. It validates daemon setup against real OS behavior.

## Risks And Test Signals
The fixed username can conflict with existing users or parallel tests. The strongest signal is that a process running as the remapped root uid/gid can access a chowned directory.
