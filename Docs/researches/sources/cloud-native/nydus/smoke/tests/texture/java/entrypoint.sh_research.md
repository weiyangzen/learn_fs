# sources/cloud-native/nydus/smoke/tests/texture/java/entrypoint.sh

## Purpose
This entrypoint compiles and runs the Java texture program in container smoke tests.

## Important APIs, Types, And Functions
It runs `cd /src`, `javac Main.java`, and `java Main`. There are no functions or parameters.

## Control Flow
The caller runs the script under `sh`. It changes to the mounted source directory, compiles `Main.java`, then launches the resulting class.

## State And Persistence
Compilation writes `Main.class` in `/src`. Because `/src` is a host-mounted texture directory, this can leave a generated class file unless cleaned outside this script.

## Dependencies And Integration Points
The script is selected for `amazoncorretto` images by `tool/container.go`, requiring a JDK with `javac` and `java`.

## Risks
No `set -e` means a failed `cd` or `javac` may not stop the script before the next command, although final nonzero status should still surface if `java Main` fails. Writing `Main.class` into the mounted source tree can dirty local state.

## Test Signals
Successful script exit verifies the Java toolchain can read/write/execute the mounted texture payload.
