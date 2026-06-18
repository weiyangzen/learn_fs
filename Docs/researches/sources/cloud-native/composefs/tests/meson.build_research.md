# sources/cloud-native/composefs/tests/meson.build

## Purpose
This Meson file registers composefs test assets, shell tests, the C unit test, and optional valgrind setup.

## Important APIs, Types, And Functions
It defines fixture lists `test_assets_small`, `test_assets_small_extra`, `test_assets_should_fail`, `test_assets`, `extra_dist`, `tools_dir`, and Meson `test()` calls for units, checksums, dump filtering, random FUSE, should-fail, and `test-lcfs`.

## Control Flow
Asset lists are assembled first, extra distribution entries are populated, shell tests are registered with appropriate args/timeouts, the C test executable links with `libcomposefs`, and valgrind setup is added if found.

## State And Persistence
No runtime state. It controls build/test graph and distributed test fixtures.

## Dependencies And Integration Points
Consumes built tools, `libcomposefs`, test scripts, fixture assets, and optional valgrind. It is entered by top-level Meson.

## Risks
The `test-checksums.sh` script expects four arguments but this Meson invocation passes three in the inspected file, while the script body does not use the fourth variable. Fixture lists must remain synchronized with asset files and expected checksums.

## Test Signals
This is the central test registration for the subset and maps implementation risks to automated checks.
