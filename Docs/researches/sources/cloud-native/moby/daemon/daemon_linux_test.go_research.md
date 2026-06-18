# sources/cloud-native/moby/daemon/daemon_linux_test.go

## Purpose
Tests Linux-specific mount cleanup, root propagation cleanup, interface address discovery, and Linux isolation validation.

## Important APIs, Types, And Functions
- `mountsFixture` and `mountsFixtureOverlay2` simulate `/proc/self/mountinfo` for aufs and overlay2 cases.
- `TestCleanupMounts`, `TestCleanupMountsByID`, and `TestNotCleanupMounts` validate cleanup filtering.
- `TestValidateContainerIsolationLinux` checks Hyper-V isolation rejection on Linux.
- `TestShouldUnmountRoot` exercises root unmount eligibility.
- `TestRootMountCleanup` exercises real mount propagation and cleanup as root.
- `TestIfaceAddrs` and `createBridge` verify netlink address lookup.

## Control Flow
The tests inject fake unmount callbacks into `cleanupMountsFromReaderByID` to count target matches, table-drive `shouldUnmountRoot`, and use temporary mountpoints for root propagation cleanup. Network tests create a bridge in a test OS namespace and compare returned IPv4/IPv6 addresses.

## State And Persistence
Most tests are in-memory fixture driven. Root and netlink tests create temporary directories, mounts, and bridge interfaces, with cleanup deferred by the test harness. Root-only tests skip when not privileged.

## Dependencies And Integration Points
Depends on Linux mount APIs, mountinfo parsing, netlink, test namespace helpers, container isolation validation, and daemon config root/exec-root marker conventions.

## Risks And Edge Cases
Root-required tests may be skipped in unprivileged CI, leaving propagation behavior less covered. Fixture-based cleanup tests are precise for known mount formats but may miss future mount path patterns.

## Test Signals
Failures indicate over-broad or under-broad stale mount cleanup, incorrect daemon-root unmount decisions, Linux accepting unsupported isolation, or broken netlink address enumeration.
