# sources/distributed-fs/ceph-client/lib/min_heap.c

Purpose: Provides exported out-of-line wrappers for generic min-heap inline helpers.

Important APIs/types/functions: Exports `__min_heap_init`, `__min_heap_peek`, `__min_heap_full`, `__min_heap_sift_down`, `__min_heap_sift_up`, `__min_heapify_all`, `__min_heap_pop`, `__min_heap_pop_push`, `__min_heap_push`, and `__min_heap_del`.

Control flow: Every function delegates directly to the matching `_inline` helper with heap, element size, callbacks, and user args.

State and persistence: Heap state is caller-owned in `min_heap_char` storage.

Dependencies/integration: Depends on `linux/min_heap.h`; exports make heap helpers available to modules even when inline bodies are not sufficient.

Risks: Correctness depends on caller-provided callbacks and element sizes; this file adds no validation beyond inline helper behavior.

Test signals: No local tests; coverage comes from min-heap users and any generic heap tests.
