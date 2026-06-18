# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glfs-message-id.h

## Purpose
Allocates stable log message ID ranges and defines the macro system for typed GlusterFS log messages.

## APIs, Types, and Functions
`GLFS_MSGID_BASE` and `GLFS_MSGID_SEGMENT` define global message-space layout. `GLFS_MSGID_COMP()` allocates component ranges in `_msgid_comp`. Legacy `GLFS_MSGID()` and migrated `GLFS_MIG()` support older numeric IDs. New typed messages use `GLFS_COMPONENT()`, `GLFS_NEW()`, `GLFS_OLD()`, and `GLFS_GONE()`, which generate message structs, inline capture functions, process functions, static range assertions, and formatted `_gf_log()` calls. Field helpers include `GLFS_U32/I32/U64/I64`, `GLFS_ERR`, `GLFS_RES`, `GLFS_RAW`, `GLFS_STR`, `GLFS_FUNC`, `GLFS_UUID`, and `GLFS_PTR`. Component segments are reserved for glusterfsd, libglusterfs, rpc, cli, glusterd, AFR, DHT, POSIX, quota, EC, io translators, and many others.

## Control Flow, State, and Persistence
This is compile-time code generation. `__COUNTER__` assigns IDs relative to component bases, `_Static_assert` prevents overruns, and inline message constructors defer formatting data preparation until logging is invoked. IDs are persistent external contracts for logs and tooling.

## Dependencies and Integration
Depends on logging, standard integer formatting, `strerror()`, and UUID formatting. Used by component message catalogs such as `libglusterfs-messages.h`.

## Risks and Test Signals
Risks include reordering or deleting IDs, exhausting a segment, macro argument mistakes, compiler-extension portability, and inconsistent field semantics. Test signals include compile-time static assertions, generated log output tests, ID-stability reviews, and builds across supported compilers.
