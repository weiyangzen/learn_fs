# sources/compression/zstd/.github/workflows/dev-long-tests.yml

Purpose: long-running pull-request workflow for expensive zstd validation on `dev`, `release`, and `actionsTest` branches.

Important behavior: jobs run `make all`, full `make test` on Linux/macOS/32-bit, large dictionary tests, no-intrinsics fuzzing, TSAN/UASAN/MSAN/ASAN fuzz and zstream/test-zstd variants, GCC 8 sanitizer jobs, regression under sanitizers, QEMU ARM fuzz, Valgrind stack/fuzzer checks, MSYS2 MinGW long fuzzing, and OSS-Fuzz CIFuzz builds/runs for address, undefined, and memory sanitizers. Concurrency cancels older runs for the same ref.

State, dependencies, and integration: state includes apt-installed compilers/tools, downloaded packages, sanitizer runtimes, QEMU, MSYS2 packages, OSS-Fuzz outputs, and uploaded crash artifacts. Integration spans make targets in root/tests/fuzz/regression and external OSS-Fuzz actions.

Risks and test signals: long wall time and external package repositories are the main flake sources. The workflow is the strongest signal for memory safety, race detection, fuzz stability, dictionary-heavy behavior, and emulator portability.
