# sources/distributed-fs/ceph-client/include/media/frame_vector.h

## Purpose
Defines `struct frame_vector`, the small container used by media memory paths to store pinned user virtual memory as either `struct page *` entries or raw PFNs. The source was read as a complete header.

## Important APIs, Types, and Functions
Exports `frame_vector_create()`, `frame_vector_destroy()`, `get_vaddr_frames()`, `put_vaddr_frames()`, `frame_vector_to_pages()`, `frame_vector_to_pfns()`, and inline accessors `frame_vector_count()`, `frame_vector_pages()`, and `frame_vector_pfns()`. The core fields are `nr_allocated`, `nr_frames`, `got_ref`, `is_pfns`, and flexible array `ptrs[]`.

## Control Flow
Callers allocate a vector, pin or collect frames with `get_vaddr_frames()`, convert between PFN and page views as needed, then release pins with `put_vaddr_frames()` and destroy the vector. The inline accessors lazily convert representation before returning typed pointers.

## State and Persistence Behavior
State is transient per pinning operation. `got_ref` tracks whether page references were obtained and therefore whether release work is required. `is_pfns` tracks the current interpretation of `ptrs[]`.

## Dependencies and Integration Points
Integrates with memory management, page/PFN conversion, and media/videobuf paths that need user-memory frame pinning without permanently committing to page-backed storage.

## Risks
Misinterpreting `ptrs[]`, leaking pinned pages, converting invalid PFNs to pages, or using the vector after `put_vaddr_frames()` can corrupt memory-management state. Callers must respect partial pin counts and error pointers from `frame_vector_pages()`.

## Test Signals
Compile coverage for media memory users, pin/unpin tests for writable and read-only ranges, PFN-only mapping tests, conversion failure tests, and leak/refcount checks around short pins and error unwinds.
