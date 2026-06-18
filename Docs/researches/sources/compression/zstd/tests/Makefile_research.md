# sources/compression/zstd/tests/Makefile

## Purpose

This Makefile builds zstd test programs and defines the main test targets for fuzzing, streaming, benchmarking, CLI tests, compatibility checks, valgrind runs, and format-specific coverage.

## Important APIs, Types, and Functions

It imports `../lib/libzstd.mk`, derives zstd object lists, configures multithread flags, and defines targets including `fullbench`, `fuzzer`, `zstreamtest`, sanitizer variants, `paramgrill`, `datagen`, `decodecorpus`, `poolTests`, `checkTag`, `test`, `check`, `test-cli-tests`, `update-cli-tests`, `test32`, `test-all`, `test-valgrind`, `test-lz4`, and clean helpers. Variables such as `ZSTD_LEGACY_SUPPORT`, `DEBUGLEVEL`, `PYTHON`, `FUZZERTEST`, `ZSTREAM_TESTTIME`, `QEMU_SYS`, and `CLI_TEST_ARGS` tune behavior.

## Control Flow, State, and Persistence

Build targets compile library objects into local test executables, often with separate multithread and 32-bit object prefixes. Test targets build prerequisites, run binaries with configured time limits, invoke `playTests.sh` and `cli-tests/run.py`, and remove generated artifacts through `clean`.

## Dependencies and Integration Points

It integrates the zstd library, programs directory, fuzz directory, CLI test harness, Python scripts, shell tools, QEMU prefixes, valgrind, diff/gdiff, and platform-specific OS detection.

## Risks and Test Signals

Risks include fragile platform filters, unavailable 32-bit toolchains, dynamic-library targets documented as broken, long-running fuzz tests, and generated temporary files. Passing `make check`, `make test`, `make test32`, `make test-cli-tests`, and selected sanitizer/valgrind targets are the primary signals.
