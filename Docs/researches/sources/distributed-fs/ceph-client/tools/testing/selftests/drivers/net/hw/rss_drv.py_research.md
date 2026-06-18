
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_drv.py`

## Purpose
Tests driver-specific RSS indirection table sizing and dynamic resize semantics for the main RSS context and additional contexts.

## Important APIs, Types, And Functions
- `_is_power_of_two()`, `_get_rss()`, `_test_rss_indir_size()`, `_maybe_create_context()`, and `_require_dynamic_indir_size()` are shared helpers.
- `indir_size_4x()` enforces at least four table entries per queue.
- `resize_periodic()` verifies a periodic user table folds and unfolds across channel changes.
- `resize_below_user_size_reject()` validates that channel shrink below netlink user-size is rejected.
- `resize_nonperiodic_reject()` and `resize_nonperiodic_no_corruption()` validate rejection and state preservation for nonperiodic tables.

## Control Flow
Each test is expanded over main and additional context variants. The code reads channel limits, restores original channel counts via `defer()`, optionally creates an RSS context via netlink, then changes channel counts with ethtool while reading the table back through `ethtool -x`.

## State And Persistence
Mutates combined channel count, main RSS table, and additional RSS contexts. Main-context table changes are reset to default where needed; created contexts are deleted via deferred `rss_delete_act()`.

## Dependencies And Integration Points
Depends on `NetDrvEnv`, `EthtoolFamily`, ethtool CLI, ethtool netlink RSS context create/delete, and drivers that dynamically resize indirection tables.

## Risks
The tests intentionally skip devices without dynamic table sizing. Queue-count changes can affect the whole interface, so a failed resize path must leave both channel count and RSS table unchanged.

## Test Signals
Expected pass signals are minimum table length, exact folded/unfolded periodic patterns, `CmdExitFailure` on invalid shrink attempts, unchanged table contents after a failed resize, and unchanged channel count after rejection.
