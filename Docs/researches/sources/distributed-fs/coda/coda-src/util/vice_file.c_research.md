# sources/distributed-fs/coda/coda-src/util/vice_file.c

## Purpose
Implements path construction for files under the configured Coda server `/vice` tree.

## Important APIs, Types, And Functions
`vice_dir_init()` stores the root directory in static `vicedir`. `vice_config_path()` calls internal `vice_filepath()` to return either the root or a root/name joined path.

## Control Flow
Initialization copies the configured directory into a bounded static buffer. Path lookup alternates between two static `volpath` buffers so calls such as `rename(path1, path2)` can use two returned paths at once.

## State And Persistence
State is process-global static path buffers. No filesystem state is changed by this file.

## Dependencies And Integration Points
Depends on `MAXPATHLEN`, `snprintf`, `CODA_ASSERT`, and `coda_string`. Used by server code such as `updatesrv` to locate `db`, `misc`, and other vice-tree files.

## Risks
Returned pointers refer to shared static buffers and are not thread-safe. Only two generated paths are stable at once. `vice_dir_init()` must be called before path construction.

## Test Signals
Initialize custom roots, request root and nested paths, call twice in one expression use case, exceed `MAXPATHLEN` under assertion builds, and test concurrent callers if any exist.
