# File Research: sources/block-storage/linux-dm/drivers/md/dm-mpath.h

## Purpose

`dm-mpath.h` defines the small public interface shared by the multipath target and path selectors.

## API

`struct dm_path` contains a read-only `struct dm_dev *dev` for the underlying path and an opaque `void *pscontext` reserved for the active path selector. Selectors use `pscontext` to attach per-path state such as list nodes, counters, throughput data, CPU masks, or historical latency statistics.

The header also declares `dm_pg_init_complete(struct dm_path *path, unsigned err_flags)`, a completion callback interface for hardware path-group initialization users.

## Invariants And Risks

- `dev` ownership remains with the multipath target; selectors must not release it.
- `pscontext` has exactly one owner: the selector instance that accepted the path.
- Selectors must clear/free any `pscontext` allocations in their destroy path.

## Test Focus

Check selector add/fail/reinstate/destroy paths for correct `pscontext` lifetime and ensure no selector assumes more than the two fields exported in `dm_path`.
