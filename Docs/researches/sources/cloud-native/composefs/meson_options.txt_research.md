# sources/cloud-native/composefs/meson_options.txt

## Purpose
This file declares user-visible Meson feature options for optional man-page generation and FUSE support.

## Important APIs, Types, And Functions
Options are `man` and `fuse`, both `feature` type with default `auto`. `man` controls use of `go-md2man`; `fuse` controls the `fuse3 >= 3.10.0` dependency and FUSE tool support.

## Control Flow
Top-level `meson.build` reads these options through `get_option`.

## State And Persistence
No runtime state. These options persist in Meson build configuration.

## Dependencies And Integration Points
`man/meson.build` is entered only when `go-md2man` is found according to the option. FUSE dependency status is exposed in `config.h` as `HAVE_FUSE3`.

## Risks
Setting either option to `enabled` makes missing dependencies fatal. Default `auto` can produce different build surfaces across machines.

## Test Signals
FUSE-dependent tests skip or reduce behavior when `/dev/fuse` and capabilities are unavailable; build option effects are mostly validated by target presence.
