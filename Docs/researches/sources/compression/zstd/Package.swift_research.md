# sources/compression/zstd/Package.swift

Purpose: Swift Package Manager manifest exposing zstd's C library as a Swift-consumable package product.

Important behavior: declares package `zstd`, supports macOS 10.10, iOS 9, and tvOS 9, and exports one library product `libzstd`. The single target points at `lib`, includes source subdirectories `common`, `compress`, `decompress`, and `dictBuilder`, publishes headers from `.`, and adds `.` as a C header search path. Swift language version is 5, C standard is GNU11, and C++ standard is GNU++14.

State, dependencies, and integration: no external package dependencies are declared. It integrates SwiftPM with the repository's C source layout and public headers.

Risks and test signals: source list maintenance is the main risk; new required lib subdirectories must be reflected here. SwiftPM builds may expose header visibility or platform-availability problems not covered by make/CMake workflows unless explicitly tested downstream.
