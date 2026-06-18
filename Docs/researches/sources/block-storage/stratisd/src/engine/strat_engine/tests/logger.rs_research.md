# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/logger.rs

## Purpose
Provides one-time logger initialization for tests.

## Main Components
- `LOGGER_INIT: Once`
- `init_logger()`

## Behavior
`init_logger()` wraps `env_logger::init` in `Once::call_once()` because multiple logger initialization attempts return errors. Test harnesses call this before running loopbacked or real-device tests.

## Research Notes
This is intentionally minimal infrastructure to avoid duplicate logger initialization across many tests.
