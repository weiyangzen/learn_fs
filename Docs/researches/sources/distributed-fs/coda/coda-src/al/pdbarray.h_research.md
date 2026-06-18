# sources/distributed-fs/coda/coda-src/al/pdbarray.h

Purpose: Declares the `pdb_array` container and operations used throughout the protection database implementation.

Important APIs/types: `pdb_array` with `size`, `memsize`, and `data`; iterator offset typedef `pdb_array_off`; mutators, merge/copy, pack/unpack, iteration, and formatting routines.

Control flow and state model: The API assumes the implementation keeps `data` sorted and duplicate-free. Iteration uses a caller-owned integer offset initialized by `pdb_array_head` and advanced by `pdb_array_next`.

Persistence and integration: Pack/unpack are the bridge between in-memory PDB profile arrays and on-disk serialized profile records. The header is included by `pdb.h` and any caller needing direct list inspection.

Risks and test signals: The API exposes raw `data`, so callers can break sort and uniqueness invariants. No capacity is passed into `pdb_array_to_array`; callers must allocate at least `size` elements.
