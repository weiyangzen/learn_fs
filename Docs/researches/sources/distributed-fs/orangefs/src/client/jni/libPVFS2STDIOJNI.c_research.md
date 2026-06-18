<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2STDIOJNI.c -->
# sources/distributed-fs/orangefs/src/client/jni/libPVFS2STDIOJNI.c

## Purpose

`libPVFS2STDIOJNI.c` implements native methods for `PVFS2STDIOJNI`, exposing C stdio and directory/user/group helpers to Java. The Hadoop adapter relies on this file for directory listing, recursive directory deletion, and translating uid/gid values into names.

## Important APIs, Types, and Functions

Private helpers resolve users and groups: `get_groupname_by_gid`, `get_username_by_uid`, `get_gid_by_groupname`, and `get_uid_by_username`. JNI exports wrap `FILE*` operations such as `fopen`, `fdopen`, `fclose`, `fflush`, `fread`, `fwrite`, `fseek`, `ftell`, `fgets`, `fputs`, unlocked variants, `tmpfile`, and buffer controls; directory APIs such as `opendir`, `fdopendir`, `readdir`, `closedir`, `rewinddir`, `seekdir`, `telldir`, and `dirfd`; helper APIs `getEntriesInDir`, `recursiveDeleteDir`, `getUsername`, `getGroupname`, `getUid`, and `getGid`; and `fillPVFS2STDIOJNIFlags` for constants.

## Control Flow

Wrappers convert Java strings/arrays to native buffers, call stdio or directory routines, convert results back to Java primitives, strings, byte arrays, or `ArrayList` objects, and print diagnostics through common JNI macros. `getEntriesInDir` opens a directory, skips `.`/`..`, appends entry names to a Java `ArrayList`, and closes the directory. `recursiveDeleteDir` walks a directory tree and removes children before the parent.

## State, Persistence, and Concurrency

The file mutates persistent filesystem state through remove/recursive delete and writes through `FILE*`. Java stores native `FILE*`/`DIR*` pointers as `jlong`, so caller discipline controls lifetime and thread safety. User/group lookups consult system account databases and are not OrangeFS-specific.

## Dependencies and Integration Points

It depends on libc stdio/dirent/pwd/group APIs, JNI, the common JNI header, and matching Java native declarations. `OrangeFileSystem.getFileStatus` uses user/group lookup; `listStatus` uses `getEntriesInDir`; recursive delete uses `recursiveDeleteDir`.

## Risks and Test Signals

Risks include pointer-as-long misuse, recursive deletion of unintended paths, fixed 32-byte user/group buffers, directory iteration races, unlocked stdio variants, and Java/native signature drift. Tests should list directories with many entries, unusual names, and permission errors; verify recursive delete on nested trees; resolve uid/gid failures; and run file read/write wrappers through EOF and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2STDIOJNI.c -->
