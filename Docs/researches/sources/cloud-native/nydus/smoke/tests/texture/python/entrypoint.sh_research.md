# sources/cloud-native/nydus/smoke/tests/texture/python/entrypoint.sh

## Purpose
This one-line shell script is the Python texture entrypoint for container smoke tests.

## Important APIs, Types, And Functions
It invokes `python -c 'print("hello")'`.

## Control Flow
The caller runs the script under `sh`; Python starts, prints `hello`, and exits.

## State And Persistence
No persistent state is written.

## Dependencies And Integration Points
`tool/container.go` mounts this file for the `python` recipe and executes it as `sh /src/entrypoint.sh`. It assumes `python` exists in the image.

## Risks
Images that expose only `python3` would fail. The script does not validate mounted file contents beyond its own readability.

## Test Signals
Successful script exit proves the Python runtime starts from the Nydus-backed container environment.
