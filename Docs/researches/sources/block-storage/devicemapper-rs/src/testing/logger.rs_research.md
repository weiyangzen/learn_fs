# File Research: sources/block-storage/devicemapper-rs/src/testing/logger.rs

## Purpose
Provides one-time logger initialization for tests.

## Key API
`init_logger()` calls `env_logger::init` behind a `Once`.

## Notes
Avoids repeated logger initialization failures across multiple tests.
