# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/dirent.cc

## Purpose

This file implements `XPlatform::Dirent::NextFile()`, the C++ directory iterator used by the portable C dirent shim.

## Important APIs, types, and functions

The only exported method is `NextFile()`, returning `std::variant<std::monostate, std::filesystem::directory_entry, std::error_code>`. The variant distinguishes successful entries, end-of-iteration, and filesystem errors without exceptions.

## Control flow, state, and persistence

If the iterator already has an error code, `NextFile()` returns that error. If the iterator equals `std::filesystem::end(dir_it_)`, it returns `std::monostate`. Otherwise it copies the current `directory_entry`, advances the iterator with `increment(error_code&)`, and returns the copied entry. State is the internal filesystem iterator and last error code; it does not persist outside the object.

## Dependencies and integration points

The implementation depends on C++17 `<filesystem>`, `<system_error>`, and `<variant>`, plus `x-platform/dirent.h`. It feeds the C API `readdir()` implementation and any C++ callers that want a non-throwing one-pass directory scan.

## Risks and test signals

The constructor in the header initializes `directory_iterator` with an error code, but severe filesystem conditions may still behave differently across platforms. Copying `directory_entry` before incrementing avoids invalidation surprises. Test signals are empty directory iteration, invalid path error propagation, permission-denied behavior, and stable entry names through the C shim.
