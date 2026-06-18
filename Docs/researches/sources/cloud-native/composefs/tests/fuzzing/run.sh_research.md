# sources/cloud-native/composefs/tests/fuzzing/run.sh

## Purpose
This shell script configures and runs honggfuzz against `tools/mkcomposefs` with sanitizers and a bubblewrap sandbox.

## Important APIs, Types, And Functions
It invokes `./configure` with `hfuzz-clang`, UBSan/ASan, static build flags, and sanitizer coverage flags; runs `make -j $(nproc)`; then launches `honggfuzz --verifier` against inputs under `tests/fuzzing`.

## Control Flow
The script is linear and uses `set -xeuo pipefail`: configure, build, sandbox, fuzz.

## State And Persistence
It creates build outputs and fuzzing runtime artifacts outside the Meson path. It does not alter source inputs.

## Dependencies And Integration Points
Depends on autotools-style `configure`, honggfuzz, hfuzz-clang, bubblewrap, and sanitizer runtime support. It targets `mkcomposefs` rather than library APIs directly.

## Risks
This path may be stale if the project is Meson-first. It requires privileged/sandbox tooling and can consume significant CPU.

## Test Signals
Fuzzing seeds include crash/regression assets referenced by Meson tests, such as honggfuzz-derived dump fixtures.
