# sources/compression/zstd/tests/cli-tests/determinism/setup_once

## Purpose
Suite-level setup for determinism tests. It creates a stable matrix of generated inputs covering sizes and compressibility percentages.

## APIs, control flow, and integration
It sources platform helpers, creates `files/`, and writes `datagen` outputs for sizes 0 through 1,000,000 bytes plus `-P0`, `-P10`, `-P25`, `-P50`, `-P75`, `-P90`, and `-P100` at size 10,000. `run.py` runs this once per determinism suite scratch directory before individual test setup.

## State, dependencies, risks, and test signals
The state persists for the suite and is copied into each test. Dependencies are deterministic `datagen` defaults and platform helper availability. Risks are fixture drift causing checksum updates and disk usage from copying. Setup success enables the downstream exact-output determinism checks.
