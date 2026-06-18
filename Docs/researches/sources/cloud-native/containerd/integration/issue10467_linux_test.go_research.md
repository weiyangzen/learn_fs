# sources/cloud-native/containerd/integration/issue10467_linux_test.go

## Purpose

This Linux upgrade regression test verifies migration of sandbox metadata from an old incorrect root bucket layout into the proper namespace bucket layout. It reproduces state from containerd v1.7.20 and validates current migration.

## Important APIs, Types, And Functions

- `TestIssue10467` is the only test.
- External helpers `downloadReleaseBinary`, `oneSevenCtrdConfig`, `currentReleaseCtrdDefaultConfig`, and `shouldManipulateContainersInPodAfterUpgrade` prepare and verify upgrade scenarios.
- `bbolt.Open` inspects `meta.db` buckets before and after migration.

## Control Flow

The test downloads v1.7.20, starts that containerd with `ENABLE_CRI_SANDBOXES=yes`, creates pods/containers through an upgrade case helper, stops the old process, and opens the bolt metadata database to assert a root `k8s.io` bucket exists. It then writes current config, starts current containerd on the same work directory, copies `meta.db`, asserts the root `k8s.io` bucket no longer exists, and runs the upgrade verification function against the migrated state.

## State And Persistence Behavior

The central persisted state is containerd's bolt metadata database under the temporary root. The test intentionally creates old-format metadata and verifies current startup migrates it.

## Dependencies And Integration Points

It depends on release binary download, old/current containerd config helpers, CRI runtime/image services, `go.etcd.io/bbolt`, and continuity file copying.

## Risks And Edge Cases

Network or release availability can break setup. The test assumes v1.7.20 preserves the old bucket shape. Direct bolt inspection is tightly coupled to metadata schema.

## Test Signals

Passing confirms current containerd migrates old sandbox metadata and existing pods/containers remain usable after upgrade.
