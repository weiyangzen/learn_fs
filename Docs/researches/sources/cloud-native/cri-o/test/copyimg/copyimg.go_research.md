# sources/cloud-native/cri-o/test/copyimg/copyimg.go

## Purpose
Small CLI utility for integration tests to copy container images between transports and CRI-O storage.

## Important APIs, Types, And Functions
`main()` builds a `urfave/cli/v2` app with flags for debug logging, storage root/runroot/driver/options, signature policy, image name, additional name, import source, and export target. It uses `copy.Image`, containers/image signatures, storage transport, and containers/storage.

## Control Flow
After reexec handling, the CLI validates root/runroot pairing when storage image operations are requested, opens a store, configures the storage transport, parses image references, loads signature policy, creates a policy context, and then imports, tags, exports, or directly copies image references depending on supplied flags.

## State And Persistence
May create or mutate a containers/storage graphroot/runroot, add image names, and write exported image data to target transports/directories. Cleans up store and policy contexts on exit.

## Dependencies And Integration Points
Used by `common.sh` and `helpers.bash` to pre-cache and import images into per-test CRI-O storage. Integrates with `go.podman.io/image/v5` and `go.podman.io/storage`.

## Risks And Test Signals
Uses `log.Fatalf` inside the CLI action, which exits the process rather than returning errors. Flag combinations with only import or only export and no image-name are accepted but do nothing. Correct behavior is exercised by integration tests that rely on image setup.
