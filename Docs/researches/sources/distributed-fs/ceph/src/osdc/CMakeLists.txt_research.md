# sources/distributed-fs/ceph/src/osdc/CMakeLists.txt

## Purpose

`src/osdc/CMakeLists.txt` defines the static `osdc` library target for a small subset of Ceph OSD client support sources.

## Important APIs, types, and functions

- `set(osdc_files Filer.cc ObjectCacher.cc)` lists sources compiled into this target.
- A comment states that `error_code.cc`, `Objecter.cc`, and `Striper.cc` are part of `libcommon` rather than this static library.
- `add_library(osdc STATIC ${osdc_files})` creates the `osdc` static library.
- `target_link_libraries(osdc ceph-common)` links it against `ceph-common`.
- `if(WITH_EVENTTRACE) add_dependencies(osdc eventtrace_tp) endif()` adds an optional build dependency when event tracing is enabled.

## Control flow

CMake configures the source list, creates the target, links common Ceph support, and conditionally orders eventtrace tracepoint generation before building `osdc`.

## State and persistence behavior

No runtime state is involved. The file affects generated build system state: target definitions, link dependencies, and optional build ordering.

## Dependencies and integration points

This build fragment integrates with Ceph's top-level CMake, `ceph-common`, optional `WITH_EVENTTRACE`, and source files under `src/osdc`. Downstream targets may link against `osdc` to use `Filer` and `ObjectCacher`.

## Risks

Adding sources here that are already compiled into `libcommon` can produce duplicate symbols or target layering problems. Omitting a required source creates unresolved references for consumers. The eventtrace dependency is conditional; eventtrace-generated artifacts must match the target's actual include/use pattern.

## Test signals

Build tests should configure both `WITH_EVENTTRACE=ON` and `OFF`, build `osdc`, and build downstream consumers. Link tests should catch accidental movement of `Objecter`, `Striper`, or error-code sources between `osdc` and `ceph-common`.
