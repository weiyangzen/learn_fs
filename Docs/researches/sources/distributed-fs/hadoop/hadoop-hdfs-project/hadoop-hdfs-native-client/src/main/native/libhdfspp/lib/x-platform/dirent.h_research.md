# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/dirent.h

## Purpose

This header declares `XPlatform::Dirent`, a C++ one-shot directory iteration helper that abstracts platform filesystem differences for libhdfspp.

## Important APIs, types, and functions

`Dirent(const std::string &path)` constructs a `std::filesystem::directory_iterator` with an error-code sink. `NextFile()` returns either end-of-iteration, a `std::filesystem::directory_entry`, or an error code. The class uses default copy/move/destructor operations and stores `dir_it_err_` plus `dir_it_`.

## Control flow, state, and persistence

Iteration is stateful and advances on every `NextFile()` call. The object is intended for one complete pass through a directory. It keeps the latest iterator error in memory and does not persist anything to disk.

## Dependencies and integration points

It depends on C++17 filesystem and feeds both C++ platform utilities and the C `dirent` compatibility wrapper. It lets libhdfspp support Windows builds without a POSIX dirent implementation.

## Risks and test signals

Because the rule-of-five operations are defaulted, copying a `Dirent` copies iterator state, which may be surprising or implementation-dependent. Error reporting depends on filesystem error-code behavior. Directory iteration tests should cover invalid paths, empty directories, multiple entries, and copying or moving only if consumers rely on that.
