<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/cleanup_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/cleanup_orangefs.sh

## Purpose
Deletes all files under the example OrangeFS storage directory.

## Important APIs, Types, And Functions
Changes to the script directory, sources `setenv`, and runs `rm -rf ${ORANGEFS_STORAGE_DIR}/*`.

## Control Flow
Straight-line cleanup with no tracing or error checks.

## State And Persistence
Destructively removes OrangeFS server storage contents for the example deployment.

## Dependencies And Integration Points
Depends on sibling `setenv` defining `ORANGEFS_STORAGE_DIR`. Used by reset/relaunch scripts before reinitializing storage.

## Risks And Test Signals
Risks include unquoted destructive path expansion, empty or wrong `ORANGEFS_STORAGE_DIR`, glob behavior with hidden files, and no service-state check before deletion. Test signals are running only after server stop, verifying storage is empty, and ensuring reset can reinitialize successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/cleanup_orangefs.sh -->
