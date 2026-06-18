# sources/cloud-native/moby/daemon/volumes_unit_test.go

## Purpose
Unit coverage for legacy `--volumes-from` parsing through the daemon mount parser.

## Important APIs and Types
Contains `TestParseVolumesFrom`, using `volumemounts.NewParser().ParseVolumesFrom`.

## Control Flow, State, and Persistence
The test parses empty input, plain container IDs, read-write and read-only suffixes, and an invalid mode. It verifies container ID extraction, default `rw`, explicit `ro`/`rw`, and error handling.

## Dependencies, Integration Points, Risks, and Test Signals
This guards the first overlay path in `registerMountPoints`, where volumes inherited from another container can replace earlier mountpoints. It does not create daemon state or volumes; the signal is parser contract stability. Risks outside this test include actual source container lookup, reference acquisition for anonymous volumes, and destination conflict cleanup.
