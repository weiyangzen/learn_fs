# File Research: sources/block-storage/kvdo/vdo/data-vio-pool.h

## Purpose
Declares the `data_vio_pool` lifecycle, bio launch, release, drain/resume, diagnostics, and statistics APIs.

## Public API
- Creation/destruction:
  - `make_data_vio_pool()`
  - `free_data_vio_pool()`
- I/O:
  - `vdo_launch_bio()`
  - `release_data_vio()`
- Admin:
  - `drain_data_vio_pool()`
  - `resume_data_vio_pool()`
- Diagnostics/statistics:
  - `dump_data_vio_pool()`
  - active/limit/max getters for discards and requests
  - `set_data_vio_pool_discard_limit()`

## Research Notes
The header exposes only pool-level operations; internal limiter and queue details stay private in `data-vio-pool.c`.
