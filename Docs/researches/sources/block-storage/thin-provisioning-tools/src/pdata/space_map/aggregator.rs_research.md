# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/aggregator.rs

Defines a concurrent, region-based reference-count aggregator. `Region` abstracts increment, lookup, set, test-and-inc, memory sizing, and allocation count. `U32Region` stores counts adaptively as `NoCounts`, `Bits`, `U8s`, `U16s`, or `U32s`, upgrading when duplicate hits or count overflows require wider representation.

`RestrictedTwoRegion` stores saturated 0/1/2 counts using two bits per entry. `AggregatorImpl<R>` shards entries into 1024-block mutex-protected regions, batches sorted increments by region, supports `lookup`, `test_and_inc`, `set_batch`, `diff`, representation-size accounting, and `RefCount` integration. `SpaceMap` allocation APIs are stubbed with `todo!()`.

Tests cover representation upgrades, single/multi-region increments, concurrent increments, lookup bounds/partial reads, test-and-inc seen-bit behavior, set upgrades/allocation tracking, mixed operations, and restricted-two saturation semantics.
