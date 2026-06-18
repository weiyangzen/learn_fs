# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_schemes_tried_regions_wss_estimation.py

## Purpose

`sysfs_update_schemes_tried_regions_wss_estimation.py` verifies DAMON tried-bytes based working-set-size estimation is close to the synthetic workload size.

## Important APIs, Types, and Functions

It uses `access_memory` in repeat mode, `_damon_sysfs.Kdamonds`, `DamosAccessPattern`, `update_schemes_tried_bytes()`, and percentile/error calculations.

## Control Flow

`pass_wss_estimation()` runs a two-region workload for a given region size, starts vaddr DAMON with a hot/old access pattern, collects up to 40 tried-byte samples, stops DAMON, sorts samples, and checks 50th and 75th percentile errors are within 20 percent. `main()` tries region sizes from 10 MiB up to 160 MiB, accepting the first passing size because large TLBs can hide smaller working sets.

## State and Persistence Behavior

It starts/stops DAMON and workload processes for each attempted size and stores samples in memory.

## Dependencies and Integration Points

It depends on the access workload, DAMON vaddr sampling, tried-bytes updates, and architecture behavior around TLB/access tracking.

## Risks and Edge Cases

The test is inherently noisy and compensates by retrying larger working sets. It can consume up to hundreds of MiB and run repeated monitoring sessions.

## Test Signals

Success prints acceptable percentile errors for one size. Failure prints unacceptable samples for all attempted sizes and exits 1.
