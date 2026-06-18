# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/archivestore.h

## Purpose
Defines the external archive-store ABI consumed by the CVLT plugin to integrate with `libopenarchive.so`.

## Important APIs, types, and functions
Defines `archstore_desc_t`, `archstore_info_t`, `archstore_fileinfo_t`, callback info, `app_callback_t`, scan type enum, and function pointer typedefs for init, fini, read, recall, restore, archive, backup, and scan. `archstore_methods_t` aggregates the function table. `get_archstore_methods()` is the exported discovery function loaded by `dlsym()`.

## Control flow
`libcvlt.c` loads the archive library, asks for this method table, initializes a descriptor, and then calls `restore()` for recall or `read()` for remote read. Completion is delivered through callbacks or semaphores.

## State and persistence behavior
The header models archive-store identity, product/store id, file UUID/path, and descriptor-private state. Actual durable storage is managed by the external archive library.

## Dependencies and integration points
Depends on `uuid_t`, dynamic loader includes, and C scalar types. It is the hard ABI between GlusterFS CVLT plugin and Commvault/openarchive code.

## Risks and test signals
ABI breakage is the central risk. Tests should validate struct sizes and function table population against the deployed archive library, plus callback error propagation.
