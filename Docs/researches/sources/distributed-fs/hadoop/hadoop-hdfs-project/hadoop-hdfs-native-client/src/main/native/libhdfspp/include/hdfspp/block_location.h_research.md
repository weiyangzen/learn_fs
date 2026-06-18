# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/block_location.h

## Purpose
This header defines C++ value types for HDFS block-location metadata returned by libhdfs++.

## Important APIs, Control Flow, and State
`DNInfo` stores hostname, IP address, network location, xfer/info/IPC/secure-info ports, with default ports `-1` and simple getters/setters. `BlockLocation` stores corruption flag, length, offset, and a vector of `DNInfo` datanodes. `FileBlockLocation` stores total file length, last-block-complete flag, under-construction flag, and a vector of blocks. All state is in-memory value data with copy-based setters.

## Dependencies and Integration Points
`FileSystem::GetBlockLocations` returns `std::shared_ptr<FileBlockLocation>`, and `hdfs_ext.h` exposes corresponding C structs. Implementations populate these from NameNode block reports.

## Risks and Test Signals
`BlockLocation` and `FileBlockLocation` primitive fields are not initialized by explicit constructors in this header, so users can observe indeterminate values if implementations forget to set them. Tests should cover default construction, complete population, empty block lists, corrupt blocks, under-construction files, and C/C++ conversion fidelity.
