# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-gen-fops-h.py

## Purpose
Generates declarations for utime fop wrappers.

## Important APIs, Types, and Functions
- Imports `ops`, `fop_subs`, and `generate`.
- `OP_FOP_TEMPLATE` emits an `int32_t gf_utime_<name>(...)` prototype.
- `utime_ops` lists all wrappers requiring declarations.
- `gen_defaults()` iterates `ops.items()` and prints prototypes for selected names.

## Control Flow
Reads a template file from `sys.argv[1]`, replaces `#pragma generate` with generated prototype block, and prints all other lines unchanged.

## State and Persistence
No runtime state. Produces generated header artifact.

## Dependencies and Integration Points
Same generator metadata dependency as the C generator. Integrated by `Makefile.am`.

## Risks
If `utime_ops` diverges from C generator lists, compile can fail with missing declarations or definitions.

## Test Signals
Generated header should declare every function referenced in `utime.c` fops table.
