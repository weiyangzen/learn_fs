# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/mod.rs

This file defines the common internal backstore module interface for the real Stratis engine.

Module layout:
- Public submodules:
  - `v1`
  - `v2`

Trait:
- `InternalBackstore`

Required behavior:
- `device()` returns the current device-mapper device used by this tier, if any.
- `datatier_allocated_size()` returns currently allocated data-tier sectors.
- `datatier_usable_size()` returns total usable data-tier sectors.
- `available_in_backstore()` returns total unallocated usable sectors, including capped-but-unallocated and not-yet-added capacity.
- `alloc(pool_uuid, sizes)` tries to allocate multiple requested segments exactly:
  - returns `None` if the request cannot be satisfied exactly;
  - returns ordered `(start, length)` segment pairs otherwise;
  - documents metadata-changing semantics and pre/postconditions around allocation cursor bounds and contiguity.

Role in architecture:
- This is the abstraction boundary between higher-level pool logic and versioned real backstore implementations. It defines allocation and capacity semantics shared by backstore v1 and v2.
