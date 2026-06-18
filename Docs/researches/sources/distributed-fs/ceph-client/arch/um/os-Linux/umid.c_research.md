# sources/distributed-fs/ceph-client/arch/um/os-Linux/umid.c

## Purpose
Manages host-side UML instance identity directories and pid files under `~/.uml/` or `uml_dir=`.

## Important APIs, Types, and Functions
`set_umid()` records an explicit ID. `make_uml_dir()` expands `~`, normalizes a trailing slash, and creates the parent directory. `make_umid()` creates or takes over an instance directory, generating a random ID when needed. `is_umdir_used()`, `umdir_take_if_dead()`, and `remove_files_and_dir()` handle stale directories. `umid_file_name()`, `get_umid()`, `set_uml_dir()`, and `remove_umid_dir()` expose lifecycle helpers.

## Control Flow, State, and Persistence
Persistent host state is a per-instance directory containing a `pid` file. Runtime globals are `umid`, `uml_dir`, and `umid_setup`. Exitcall cleanup removes files in the instance directory and then the directory itself.

## Dependencies and Integration Points
Works with kernel `umid.c`, command-line setup, management console/socket naming, and exitcall cleanup. Uses host filesystem, pid liveness checks, and environment `$HOME`.

## Risks and Test Signals
Risks include races between stale directory removal and new mkdir, path length limits, pid reuse/liveness false positives, unsafe directory contents, and cleanup errors. Test concurrent same-umid boots, stale pid files, `uml_dir=`, missing HOME, long IDs, and shutdown cleanup.
