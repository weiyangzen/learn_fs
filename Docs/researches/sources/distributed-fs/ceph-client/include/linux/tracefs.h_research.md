# sources/distributed-fs/ceph-client/include/linux/tracefs.h

## Purpose
Declares tracefs and eventfs creation/removal APIs used by tracing infrastructure to expose control files, trace instances, and dynamic event directories.

## Important APIs, Types, And Functions
Defines `eventfs_callback`, `eventfs_release`, `struct eventfs_entry`, and forward `struct eventfs_inode`. APIs under `CONFIG_TRACING` include `eventfs_create_events_dir()`, `eventfs_create_dir()`, `eventfs_remove_events_dir()`, `eventfs_remove_dir()`, `tracefs_create_file()`, `tracefs_create_dir()`, `tracefs_remove()`, `tracefs_create_instance_dir()`, and `tracefs_initialized()`.

## Control Flow
Eventfs creates files lazily through callbacks: lookup/access iterates entry arrays, callback supplies mode, data, and file operations, and release handles callback data cleanup. Tracefs helper functions create normal files/directories and instance directories with mkdir/rmdir hooks.

## State, Persistence, And Dependencies
Runtime state is dentry/inode hierarchy and eventfs inode metadata owned by tracing. Callback data may be replaced per file. Dependencies include VFS `fs.h`, `seq_file`, and base types.

## Integration Points
Used by ftrace event directories, tracing instances, dynamic event files, and remote tracefs extensions.

## Risks And Test Signals
Risks include callback deadlocks because eventfs callbacks run under internal locks, data lifetime bugs, stale dentries after removal, and disabled-config missing prototypes. Test signals include lazy lookup tests, directory removal while files are open, instance mkdir/rmdir tests, and lockdep coverage for callback paths.
