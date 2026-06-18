# sources/distributed-fs/ceph-client/lib/linear_ranges.c

Purpose: generic helpers for mapping selector indexes to values and values back to selectors across one or more linear ranges.

Important APIs/types/functions: `linear_range_values_in_range()`, `linear_range_values_in_range_array()`, `linear_range_get_max_value()`, `linear_range_get_value()`, `linear_range_get_value_array()`, low/high selector lookup functions, and `linear_range_get_selector_within()`.

Control flow: value lookup checks selector bounds and computes `min + (selector - min_sel) * step`. Array helpers scan ranges in order. Low selector lookup finds the greatest selector whose value is less than or equal to the input; high lookup finds the smallest selector whose value is greater than or equal to the input. Zero-step ranges are special-cased.

State/persistence: stateless calculations only; no persistent storage.

Dependencies/integration: exported GPL symbols used by regulator-like drivers and any code representing hardware tables as `struct linear_range`. Depends on `linux/linear_range.h`, errno, and `DIV_ROUND_UP`.

Risks: assumes ranges are well-formed; unsigned arithmetic can wrap if `max_sel < min_sel` or values overflow. Array helpers assume range ordering is meaningful for fallback selector behavior.

Test signals: no direct tests in this subset. Good tests should cover zero-step ranges, selector boundaries, below/above range values, and overlapping or unordered arrays.
