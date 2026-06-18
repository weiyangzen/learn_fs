# sources/cloud-native/cri-o/test/common.sh

## Purpose
Common environment and image-preload helpers for CRI-O integration tests.

## Important APIs, Types, And Functions
Defines repository/test paths, binary locations, runtime and CNI defaults, security profile paths, image list, `img2dir`, `get_img`, and `get_images`.

## Control Flow
On source, computes `INTEGRATION_ROOT`, `CRIO_ROOT`, tool paths, defaults for runtime/storage/network/security config, and image CIDRs. `get_img` maps an image to an artifact directory and uses `copyimg` to import from a registry into a directory cache if absent. `get_images` preloads every image in `IMAGES`.

## State And Persistence
Persists cached image directories under `.artifacts` by default. Exports many variables consumed by BATS tests and `helpers.bash`.

## Dependencies And Integration Points
Integrates with `copyimg`, CRI-O binaries, crictl, conmon, CNI plugins, AppArmor, seccomp, CRIU, and testdata policies.

## Risks And Test Signals
The script assumes many host binaries and kernel features. Image caching reduces flakes but can hide stale image artifacts. Since it is sourced globally, variable mistakes affect every integration test.
