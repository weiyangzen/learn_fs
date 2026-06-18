# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/_damon_sysfs.py

## Purpose

`_damon_sysfs.py` is the Python object model used by DAMON tests to construct, stage, start, stop, commit, and query DAMON sysfs configurations under `/sys/kernel/mm/damon/admin`.

## Important APIs, Types, and Functions

Top-level helpers are `write_file()` and `read_file()`. The model includes `Kdamonds`, `Kdamond`, `DamonCtx`, `DamonAttrs`, `IntervalsGoal`, `DamonTarget`, `Damos`, `DamosAccessPattern`, `DamosQuota`, `DamosQuotaGoal`, `DamosWatermarks`, `DamosFilter`, `DamosFilters`, `DamosDests`, `DamosDest`, `DamosStats`, and `DamosTriedRegion`. Runtime operations include `start()`, `stop()`, `commit()`, `commit_schemes_quota_goals()`, `update_schemes_tried_regions()`, `update_schemes_tried_bytes()`, `update_schemes_stats()`, and `update_schemes_effective_quotas()`.

## Control Flow

On import, it locates sysfs in `/proc/mounts` and exits skip if DAMON admin sysfs is unavailable. Object `stage()` methods write nested sysfs files in dependency order: counts first, then generated child directories, then leaf attributes. `Kdamonds.start()` writes `nr_kdamonds`, starts each kdamond, stages contexts, turns state `on`, and reads pid. Update methods write command strings to `state` and then read generated stats/tried-region/effective-quota files back into Python objects.

## State and Persistence Behavior

The library mutates DAMON sysfs globally: number of kdamonds, contexts, targets, schemes, filters, quotas, watermarks, destinations, and runtime state. It stores mirrored values in Python object attributes such as `pid`, `stats`, `tried_regions`, `tried_bytes`, and `effective_bytes`.

## Dependencies and Integration Points

It depends on DAMON sysfs ABI, root permissions, and Python file I/O. Other DAMON tests import it as the canonical control API, making it the integration layer between test logic and kernel DAMON state.

## Risks and Edge Cases

Several constructors use mutable default lists/objects, which can share state across instances if tests reuse them unexpectedly. `DamosFilter.memcg_path` is assigned with a trailing comma, making it a tuple, although string formatting may hide the issue. All sysfs writes return string errors instead of exceptions, so callers must check every return.

## Test Signals

Failures from this module are error strings naming sysfs write/read failures. Successful use produces running kdamond pids and populated stats/tried-region/quota fields for higher-level assertions.
