# sources/compression/zstd/.github/workflows/commit.yml

Purpose: legacy-style commit and pull-request workflow for the `dev` branch, running short build/test suites and regression result comparison.

Important behavior: `short-tests-0` runs license checks, compiler version display, `allmost` with strict flags, C99/C11 builds, regressiontest, `make check`, and C++ compile test. `short-tests-1` installs cross compilers and validates GNU dialects, PPC/PPC64/ARM/AArch64 builds, legacy and long-match tests, and non-multithreaded lib build. `regression-test` restores a cache keyed on regression data, builds `programs/zstd`, runs regression tests, generates `results.csv`, diffs it against the committed baseline, and uploads artifacts.

State, dependencies, and integration: jobs use apt dependencies, a CircleCI-derived Docker image service, GitHub cache/artifacts, top-level make targets, tests/regression, and lib/program sub-makefiles.

Risks and test signals: `actions/cache` key syntax appears CircleCI-like inside `${{ }}`-less braces and should be watched. The regression diff is a strong guard against performance/ratio drift, while cross-compile jobs protect portability.
