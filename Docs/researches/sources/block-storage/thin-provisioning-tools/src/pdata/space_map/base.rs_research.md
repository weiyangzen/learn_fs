# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/base.rs

Defines `RefCount`, `SpaceMap`, and shared `ASpaceMap`. `CoreSpaceMap<T>` is an in-memory vector-backed refcount map with typed counters, allocation count tracking, round-robin allocation, bounds checks, and overflow checks.

Also provides `RestrictedSpaceMap` for 0/1 visited tracking, `RestrictedTwoSpaceMap` for 0/1/2 saturated counts, and `NoopSpaceMap`. Factory helpers choose `u8`, `u16`, or `u32` core maps based on maximum count. Restricted maps are used heavily by walkers to avoid duplicate visits without full refcount precision.
