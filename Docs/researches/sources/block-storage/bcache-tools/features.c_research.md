# File Research: sources/block-storage/bcache-tools/features.c

This file prints supported bcache feature flags from a `cache_sb`. It defines a feature table for incompatible features `obso_large_bucket` and `large_bucket`, then composes per-type strings for compat, ro-compat, and incompat feature sets.

It is used by detailed cache-device display in `show.c`; currently only the incompat feature table has named entries.
