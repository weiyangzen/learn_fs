# File Research: sources/cow-pools/bcachefs-tools/fs/data/update.h

## Role

Declares the data update types, option struct, runtime state struct, promote wrapper, and public update APIs.

## Update Types

`BCH_DATA_UPDATE_TYPES()` includes `other`, `copygc`, `reconcile`, `promote`, `self_heal`, `scrub`, and `scrub_no_repair`.

## `struct data_update_opts`

Carries update policy:

- Pointer masks for IO errors, pointer removal, and EC removal.
- Extra replica count and target.
- Booleans for `no_devs_have` and checksum paranoia.
- Preferred read device and read/write flags.
- Transaction commit flags.

## `struct data_update`

Owns the full move/update operation:

- Original key, btree id, options, and in-flight hash position.
- `cas[]` device references parallel to original pointers.
- Move-context list hooks and IO sequence.
- Embedded `bch_read_bio` and `bch_write_op`.
- Allocated bvec array for read/write bios.

## Promote Integration

`struct promote_op` wraps a `data_update` with promote accounting, optional async-object list index, CPU for promote limiting, and work struct.

## Exported APIs

The header exports formatting, in-flight lookup, index update, read completion, feasibility check, EC allocation failure handling, lifecycle cleanup/init, pointer-mask remapping, and filesystem table init/exit.
