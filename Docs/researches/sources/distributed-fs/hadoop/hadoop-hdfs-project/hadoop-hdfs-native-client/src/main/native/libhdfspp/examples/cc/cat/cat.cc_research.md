# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/cat/cat.cc

## Purpose
This C++ example reads an HDFS file and writes its contents to stdout using the libhdfs++ C++ API.

## Important APIs, Control Flow, and State
`main` requires a single path, parses it with `hdfs::parse_path_or_exit`, connects via `hdfs::doConnect`, opens with `FileSystem::Open`, wraps the raw `FileHandle*` in `std::unique_ptr`, and repeatedly calls `FileHandle::Read` into a static 1 MiB buffer. `Status::InvalidOffset` is treated as EOF; other non-OK statuses are fatal. It calls `google::protobuf::ShutdownProtobufLibrary` before exit.

## Dependencies and Integration Points
It includes `hdfspp/hdfspp.h`, protobuf cleanup, and `tools_common.h`. It demonstrates synchronous `FileSystem` and `FileHandle` ownership patterns: shared filesystem, raw opened handle transferred to RAII.

## Risks and Test Signals
The program passes the original `path` to `Open` rather than a normalized URI path, so accepted input forms depend on `doConnect` and filesystem path expectations. Tests should cover absolute paths, URI-like paths, empty/missing args, EOF handling, short reads, read errors, and handle deletion.
