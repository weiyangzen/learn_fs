<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/metadata.sh -->
# sources/distributed-fs/lizardfs/tests/tools/metadata.sh

Purpose: generates and prints broad metadata fixtures used by recovery, dump, mapall, shadow, and restart-consistency tests, covering files, quotas, trash, goals, trashtime, extended attributes, ACLs, snapshots, renames, truncates, and lock metadata.

Important APIs, functions, and commands: metadata APIs include `metadata_print`, `metadata_get_version`, `metadata_generate_all`, `metadata_get_all_generators`, and focused generators for files, quotas, unlink/trash, goals, trashtime, eattrs, chunks, snapshots, xattrs, ACLs, renames, uids/gids, touch, truncate, and file locks.

Control flow: The script proceeds through these visible steps: `metadata_print() {`; `assert_program_installed getfattr`; `lizardfs fileinfo "$file" | grep -v $'^\t\t' # remove "copy N" and "no valid copies"`; `lizardfs getgoal "$file"`; `lizardfs gettrashtime "$file"`; `lizardfs geteattr "$file"`.

State and persistence behavior: State is the mounted filesystem tree plus metadata-visible attributes: chunk layout, goals, trash times, eattrs, quotas, ACLs, xattrs, stat data, symlinks, changelog-derived trash events, and optional meta-mount paths.

Dependencies and integration points: Dependencies and integration points: `attr`, `getfattr`, `setfacl`, `getfacl`, `tee`, environment/config variables such as `NR`, `FILE_SIZE`, `BLOCK_SIZE`, LizardFS CLI/test helpers.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/metadata.sh -->
