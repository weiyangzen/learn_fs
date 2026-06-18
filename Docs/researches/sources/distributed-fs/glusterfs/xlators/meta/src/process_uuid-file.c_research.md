# sources/distributed-fs/glusterfs/xlators/meta/src/process_uuid-file.c

Purpose: implements the root-level virtual `process_uuid` file, exposing `this->ctx->process_uuid`.

Important APIs/types/functions: `process_uuid_file_fill()` writes the process UUID plus newline. `meta_process_uuid_file_hook()` attaches `process_uuid_file_ops`.

Control flow: `root-dir.c` exposes the `process_uuid` dirent. Lookup calls the hook, and readv calls the default file fill path.

State and persistence behavior: reads reflect the current Gluster process context UUID, cached for each open fd after materialization. No persistent storage is changed.

Dependencies and integration points: depends on Gluster xlator context and `strfd`.

Risks and edge cases: assumes `this->ctx` and `process_uuid` are valid. UUID value can reveal process identity useful for diagnostics and correlation.

Test signals: read `.meta/process_uuid`, verify it matches process context, and validate repeated offset reads.
