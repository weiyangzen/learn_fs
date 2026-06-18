# sources/distributed-fs/ceph-client/tools/perf/ui/libslang.h

## Purpose

`libslang.h` wraps inclusion of SLang headers for perf UI code and handles feature-test macro compatibility.

## Important APIs, Types, and Functions

It includes `<features.h>`, conditionally preserves/restores `_XOPEN_SOURCE`, and includes `<slang.h>`.

## Control Flow and State

No runtime behavior exists. Its state effect is preprocessor-level: it prevents SLang headers from breaking other libc feature declarations.

## Dependencies and Integration Points

Every TUI file that uses SLang primitives includes this wrapper instead of including `<slang.h>` directly.

## Risks and Test Signals

Risks are platform libc macro differences and SLang header compatibility. Build tests with supported libc/SLang versions are the primary signal.
