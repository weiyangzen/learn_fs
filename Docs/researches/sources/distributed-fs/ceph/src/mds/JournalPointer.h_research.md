# sources/distributed-fs/ceph/src/mds/JournalPointer.h

## Purpose

`JournalPointer.h` declares the small encoded object that records where an MDS rank's journal lives. It always lives at a rank-derived RADOS object location and stores the active journal inode plus an optional backup journal inode.

## Important APIs, Types, And Functions

The public data fields are `front` for the active journal and `back` for the backup journal. Constructors either accept `(node_id, pool_id)` addressing parameters or leave a default object with invalid addressing values.

`encode()`/`decode()` version 1 persist `front` and `back`. `load(Objecter*)`, blocking `save(Objecter*)`, and asynchronous `save(Objecter*, Context*)` are implemented in the `.cc` file. `is_null()` checks both journal inode fields. `dump()` emits a `journal_pointer` object with `front` and `back`. `generate_test_instances()` provides a null and non-null sample for dencoder. `get_object_id()` is private and computes the RADOS object key.

## Control Flow And Data Flow

Callers construct the object with the MDS rank and metadata pool, then load or save it through an `Objecter`. The value is passive apart from persistence helpers: MDLog owns the higher-level journal state machine and updates `front`/`back`.

## State And Persistence Behavior

Only `front` and `back` are encoded. `node_id` and `pool_id` determine where the encoded object is stored and must be supplied by the caller. A null pointer is represented as both fields zero and is valid in memory, but blocking save treats it as invalid to persist.

The class uses `WRITE_CLASS_ENCODER(JournalPointer)`, so dencoder and Ceph buffer machinery can serialize it independently of RADOS object I/O.

## Dependencies And Integration Points

Dependencies include `Formatter`, `inodeno_t`, Ceph encoding, `mdstypes.h`, `Context`, and `Objecter`. Integration points are `MDLog` startup/recovery, journal reformat, journal pointer object I/O, and diagnostics.

## Risks And Edge Cases

The default constructor is useful for decode/test instances but not for RADOS I/O because `node_id` and `pool_id` remain `-1`. The header exposes `front` and `back` as mutable public fields, so correctness depends on MDLog updating them in valid sequences. A future encoding change must preserve recovery compatibility because old pointer objects are required for MDS startup.

## Test Signals

Tests should validate dencoder coverage, `is_null()`, dump output, RADOS object load/save integration through mocked or real Objecter, and MDLog behavior when no pointer, only `front`, or both `front` and `back` are present.
