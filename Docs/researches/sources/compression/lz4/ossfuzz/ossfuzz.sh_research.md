# sources/compression/lz4/ossfuzz/ossfuzz.sh

## Purpose
`ossfuzz.sh` is the build entry point called by the Google OSS-Fuzz project to compile and export LZ4 fuzz targets.

## Important APIs, Types, And Functions
The script uses environment variables supplied by OSS-Fuzz: `CC`, `CXX`, `LIB_FUZZING_ENGINE`, `CFLAGS`, `CXXFLAGS`, and `OUT`. It sets `BUILD_ROOT` and appends a parallel job count to `MAKEFLAGS`.

## Control Flow
With `bash -eu`, the script prints build settings, sets `MAKEFLAGS` to use `nproc`, enters the `ossfuzz` directory, runs `make V=1 all`, returns to the repository root, and copies all `ossfuzz/*_fuzzer` binaries into `$OUT`.

## State, Persistence, And Dependencies
It writes build artifacts under `ossfuzz/` and final fuzzers under the OSS-Fuzz output directory. It depends on GNU make, bash, `nproc`, and the OSS-Fuzz compiler environment.

## Integration Points
OSS-Fuzz project Dockerfiles invoke this script during `build_fuzzers`. `travisoss.sh` regression-tests the script by building through OSS-Fuzz infrastructure.

## Risks
`export MAKEFLAGS+="-j$(nproc)"` assumes bash support and a working `nproc`. Copying `*_fuzzer` assumes executable names have no extension. `BUILD_ROOT` is set but not consumed by the script itself.

## Test Signals
The main validation is a full OSS-Fuzz `build_fuzzers lz4` run, plus local script execution with fake `OUT` and both empty and non-empty `LIB_FUZZING_ENGINE`.
