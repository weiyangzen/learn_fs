# sources/compression/zstd/tests/fuzz/fuzz.py

## Purpose
`fuzz.py` is the command-line orchestrator for building fuzz targets, running libFuzzer/AFL/regression modes, generating seed corpora with `decodecorpus`, minimizing corpora, zipping corpora, and listing targets.

## Important APIs, types, and command flow
Small classes/enums `InputType`, `FrameType`, and `TargetInfo` describe each target's expected corpus type and frame/block mode. `TARGET_INFO` maps all supported target names. Parsing helpers include `parse_targets()`, `targets_parser()`, `parse_env_flags()`, `compiler_version()`, and `overflow_ubsan_flags()`. Command implementations are `build()`, `libfuzzer_cmd()`/`libfuzzer()`, `afl()`, `regression()`, `gen()`, `minimize()`, `zip_cmd()`, `list_cmd()`, and `main()`.

## State, persistence, dependencies, and integration
The script derives `FUZZ_DIR`, `CORPORA_DIR`, compiler flags, sanitizer flags, `LIB_FUZZING_ENGINE`, `AFL_FUZZ`, `DECODECORPUS`, and `ZSTD` from environment defaults. `build()` shells out to `make clean` and `make -j` with constructed `CC`, `CXX`, `CPPFLAGS`, `CFLAGS`, `CXXFLAGS`, and `LDFLAGS`. Runtime commands create corpora/artifact/seed directories. `gen()` invokes `decodecorpus`, optionally trains dictionaries with `zstd --train`, and copies generated samples into the seed corpus.

## Risks and test signals
The script is shell-command heavy and trusts compiler/version output, make, zip, unzip, AFL, and corpus paths. `gen()` documentation says fuzz RNG seeds are prepended, but the current copy loop writes sample bytes directly, so seed-prefix expectations should be checked against target behavior. `minimize()` assumes a crash directory exists. Pass signals are successful builds, fuzzer process startup, regression target exits, generated corpus files, minimized corpus directories, and created zip archives.
