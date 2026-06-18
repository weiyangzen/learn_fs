# File Research: sources/block-storage/libblkid-rs/src/partition.rs

Purpose: Wraps partition tables, partitions, and partition lists returned from probing.

Key APIs:
- `BlkidParttable`: `get_type`, `get_id`, `get_offset`, `get_parent`
- `BlkidPartition`: `get_table`, `get_name`, `get_uuid`, `get_partno`, `get_start`, `get_size`, `get_type`, `get_type_string`, `get_flags`, partition kind checks
- `BlkidPartlist`: count/table lookup and partition lookup by index, part number, or device number

Implementation notes:
- Uses `PhantomData` to tie handles to a probe/list lifetime at the type level.
- Converts partition UUID strings into `uuid::Uuid`.
- Sector and byte units use wrapper types from `utils.rs`.

Notable risks:
- Pointer wrappers are non-owning and assume libblkid keeps backing memory valid.
- `get_uuid` assumes returned UUID strings parse as canonical UUIDs.
- Several read-only `BlkidPartlist` methods take `&mut self`, which is stricter than necessary.
