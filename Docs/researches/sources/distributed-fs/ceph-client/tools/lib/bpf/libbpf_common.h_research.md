<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_common.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_common.h

## Purpose
This public helper header defines common libbpf ABI annotations, deprecation machinery, lightweight macro overloading, and canonical option-struct initialization/reset helpers shared by libbpf public headers.

## APIs, Types, and Functions
The file defines `LIBBPF_API` as default symbol visibility unless already supplied, `LIBBPF_DEPRECATED()`, and `LIBBPF_DEPRECATED_SINCE()` backed by current `LIBBPF_MAJOR_VERSION` and `LIBBPF_MINOR_VERSION`. It provides preprocessor helpers `___libbpf_cat`, `___libbpf_select`, `___libbpf_nth`, `___libbpf_cnt`, and `___libbpf_overload` for argument-count dispatch. `LIBBPF_OPTS(TYPE, NAME, ...)` declares a local options struct, clears all bytes with `memset()`, sets `.sz`, and applies caller field initializers. `LIBBPF_OPTS_RESET(NAME, ...)` rebuilds an existing option variable with all bytes cleared and `.sz` reset.

## Control Flow, State, and Persistence
There is no runtime state beyond code emitted by macros at use sites. The important behavior is zeroing entire option objects, including padding, before assigning user-specified fields. This supports libbpf's convention that `.sz` defines which fields are visible to the implementation and that trailing bytes must be zero for forward compatibility.

## Dependencies and Integration
It includes `<string.h>` for `memset()` and `memcpy()` and local `libbpf_version.h` for version-gated deprecation. It is included by `libbpf.h`, `libbpf_legacy.h`, and downstream callers using libbpf option structs.

## Risks and Test Signals
Risks include compiler-specific GNU statement-expression and `typeof` usage, padding bytes not being guaranteed by all compound-literal implementations despite the explicit reset pattern, and deprecation gates needing updates as versions advance. Test signals are compile tests under supported compilers, static assertions that `.sz` is initialized, API calls with older and larger options sizes, and warnings appearing only at intended version thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_common.h -->
