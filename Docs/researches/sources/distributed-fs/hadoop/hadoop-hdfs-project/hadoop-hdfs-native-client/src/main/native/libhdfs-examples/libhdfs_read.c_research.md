# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/libhdfs_read.c

## Purpose
Minimal example program showing how to read a file through libhdfs.

## Important APIs, Types, And Functions
`main` uses `hdfsConnect`, `hdfsOpenFile` with `O_RDONLY`, `hdfsRead`, `hdfsCloseFile`, and `hdfsDisconnect`.

## Control Flow
The program expects filename, file size, and buffer size arguments, connects to default HDFS, opens the file, allocates a buffer, repeatedly reads until a short read/EOF, frees resources, closes, and disconnects.

## State, Persistence, And Dependencies
No HDFS mutation; reads remote file data. Depends on libhdfs runtime configuration, default FS, classpath, and heap allocation.

## Integration Points
Built by `libhdfs-examples/CMakeLists.txt` as `hdfs_read`.

## Risks
It reads `argv[1]` and `argv[3]` before checking `argc`, so missing args can crash. The `<filesize>` argument is documented but unused. It prints “for writing” on open-read failure.

## Test Signals
Successful run against an existing file validates basic connect/open/read/close flow; argument validation is weak.
