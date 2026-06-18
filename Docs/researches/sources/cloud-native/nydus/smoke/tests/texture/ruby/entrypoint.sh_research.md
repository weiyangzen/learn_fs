# sources/cloud-native/nydus/smoke/tests/texture/ruby/entrypoint.sh

## Purpose
This one-line shell script is the Ruby texture entrypoint for container smoke tests.

## Important APIs, Types, And Functions
It invokes `ruby -e "puts \"hello\""`.

## Control Flow
The caller runs the script under `sh`; Ruby starts, prints `hello`, and exits.

## State And Persistence
No persistent state is written.

## Dependencies And Integration Points
`tool/container.go` mounts this file for the `ruby` recipe and executes it as `sh /src/entrypoint.sh`. It assumes `ruby` exists in the image.

## Risks
The script is intentionally minimal and validates only interpreter startup plus basic mounted script access.

## Test Signals
Successful script exit proves the Ruby runtime starts from the Nydus-backed container environment.
