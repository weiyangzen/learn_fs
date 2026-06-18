<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_version.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_version.h

## Purpose
This tiny public header defines the vendored libbpf major and minor version macros used by compile-time deprecation and compatibility logic.

## APIs, Types, and Functions
It defines `LIBBPF_MAJOR_VERSION` as `1` and `LIBBPF_MINOR_VERSION` as `8`. It has no functions or types.

## Control Flow, State, and Persistence
There is no runtime behavior or state. The version macros affect preprocessing, especially `LIBBPF_DEPRECATED_SINCE()` in `libbpf_common.h`, and may be used by consumers for compile-time feature checks.

## Dependencies and Integration
It is included by `libbpf_common.h`, which is included by the public libbpf headers. It must stay synchronized with the vendored libbpf implementation and exported version functions.

## Risks and Test Signals
Risks are version skew between this header, compiled implementation functions, symbol versions, and documentation. Test signals are compile-time checks in consumers, runtime comparison against `libbpf_major_version()`, `libbpf_minor_version()`, and `libbpf_version_string()`, and packaging checks when vendoring a new libbpf release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_version.h -->
