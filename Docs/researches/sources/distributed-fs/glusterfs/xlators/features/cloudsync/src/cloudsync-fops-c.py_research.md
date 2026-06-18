# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-fops-c.py

## Purpose
Generates C implementations for cloudsync fops that follow repeated patterns: data-modifying fd operations that may recall a remote file, and loc-based status operations that refresh inode state.

## Important APIs, types, and functions
Imports `ops`, substitutions, and `generate()` from GlusterFS `generator.py`. Templates emit `cs_<name>_cbk`, `cs_resume_<name>`, and `cs_<name>` for fd data-modifying operations, and `cs_<name>_cbk`/`cs_<name>` for loc stat-like operations.

## Control flow
For fd data-modifying ops, generated fops validate inputs, allocate `cs_local_t`, read inode context, request `GF_CS_OBJECT_STATUS`, create a resume stub, wind to the child if local, or take the cloudsync inodelk and stat/repair path if remote/downloading. Callbacks update inode state and retry through `locate_and_execute()` once. Loc stat fops request object status and update/reset inode context in callbacks.

## State and persistence behavior
Generated code updates in-memory inode context and passes xdata requests to lower translators that know cloudsync object status. No durable storage is written directly.

## Dependencies and integration points
Depends on generator metadata, cloudsync helper prototypes, `GF_CS_OBJECT_STATUS`, `CS_STACK_UNWIND`, call stubs, and lower child fops. Generated functions are referenced in `cs_fops` for operations not manually implemented in `cloudsync.c`.

## Risks and test signals
Risks include operation-list drift, generated code using wrong callback error arguments, dictionary ownership mistakes, and untested multi-op combinations. Regeneration and compile tests are essential after changes to GlusterFS fop signatures.
