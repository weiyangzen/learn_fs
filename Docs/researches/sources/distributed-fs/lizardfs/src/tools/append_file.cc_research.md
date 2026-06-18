# sources/distributed-fs/lizardfs/src/tools/append_file.cc

Purpose: Implements `lizardfs appendchunks`, which appends chunk references from one or more source files into a destination file, creating the destination if needed.

Important APIs/types/functions: `append_file_run`; static `append_file_usage`; static `append_file`; legacy packet `CLTOMA_FUSE_APPEND`; response `MATOCL_FUSE_APPEND`; `open_master_conn`.

Control flow: The run function parses no options, creates/opens the destination locally, then calls `append_file` for each source. `append_file` opens master connections for destination and source, verifies both are regular files, sends a legacy packed request with destination inode, source inode, uid, and gid, then expects query id 0 and one status byte.

State and persistence: Mutates filesystem metadata/chunk layout through the master. Locally it may create the destination file before contacting the master.

Dependencies and integration: Uses legacy `datapack`, socket wrappers, `tools_common_functions`, and master registration. Integrates with master FUSE append operation.

Risks and test signals: It mixes two `open_master_conn` calls and relies on the global current-master socket, so connection lifetime is subtle. It manually allocates response buffers by server-provided length. There are no direct tests in this subset.
