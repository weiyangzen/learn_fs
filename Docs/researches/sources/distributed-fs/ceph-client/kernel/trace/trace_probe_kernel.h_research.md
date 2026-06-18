# sources/distributed-fs/ceph-client/kernel/trace/trace_probe_kernel.h

## Purpose

`trace_probe_kernel.h` supplies kernel and user memory fetch primitives for probe argument storage. It depends on `trace_probe.h` but cannot include it because of the template include model. The complete 119-line header was read.

## Important APIs, Types, and Functions

Helpers are `fetch_store_strlen_user()`, `fetch_store_strlen()`, `set_data_loc()`, `fetch_store_string_user()`, `fetch_store_string()`, `probe_mem_read_user()`, and `probe_mem_read()`. They use nofault string/memory copy APIs and update probe `__data_loc` fields.

## Control Flow

Sizing helpers compute string length first. Storage helpers expect destination `__data_loc` to encode max length and offset, copy user or kernel strings, set zero length on fault, and return the copy result. Memory reads select user access on architectures with non-overlapping address spaces when the address is below `TASK_SIZE`.

## State and Persistence Behavior

The header owns no persistent state. It mutates trace record fields and dynamic data buffers supplied by callers.

## Dependencies and Integration Points

It depends on nofault kernel/user copy APIs, `MAX_STRING_SIZE`, and data-location helpers. It is consumed by the generic fetch template and kernel-side probe implementations.

## Risks and Edge Cases

Faulting memory must not crash tracing paths. Strings can change between sizing and storage. Negative copy results become zero-length data locations. Address-space classification is architecture-dependent.

## Test Signals

Cover valid/faulting kernel and user strings, truncation, architecture address classification, invalid memory reads, and safe fault output.
