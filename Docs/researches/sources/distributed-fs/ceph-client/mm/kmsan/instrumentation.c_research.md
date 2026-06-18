# sources/distributed-fs/ceph-client/mm/kmsan/instrumentation.c

## Purpose
`instrumentation.c` implements the `__msan_*` ABI expected by Clang's `-fsanitize=kernel-memory` instrumentation. It translates compiler-inserted metadata queries, memory intrinsic wrappers, stack-variable poisoning, origin chaining, and uninitialized-use warnings into KMSAN runtime operations.

## Important APIs, Types, And Functions
Metadata getters include `__msan_metadata_ptr_for_load_n()`, `__msan_metadata_ptr_for_store_n()`, and fixed-size generated getters for 1, 2, 4, and 8 byte loads/stores. `__msan_instrument_asm_store()` handles inline assembly stores. Intrinsic wrappers are `__msan_memmove()`, `__msan_memcpy()`, and `__msan_memset()`. Origin and stack hooks include `__msan_chain_origin()`, `__msan_poison_alloca()`, `__msan_unpoison_alloca()`, `__msan_warning()`, and `__msan_get_context_state()`.

## Control Flow
Load/store metadata getters call `kmsan_get_shadow_origin_ptr()` under `user_access_save()`. Memory intrinsic wrappers preserve parameter-0 metadata for return values, execute the raw memory operation, update destination metadata, and restore return metadata. `__msan_poison_alloca()` creates a special stack-depot origin containing local-variable description and caller PCs, then poisons the stack range. `__msan_warning()` directly reports an uninitialized value use when compiler checks detect undefined behavior. Inline assembly stores best-effort unpoison output memory to avoid false positives from stores the compiler cannot model.

## State And Persistence
The file updates shadow/origin metadata and per-task/per-CPU context-state TLS fields. Stack variable origins persist through stack depot records using `KMSAN_ALLOCA_MAGIC_ORIGIN`, while chained stores use `KMSAN_CHAIN_MAGIC_ORIGIN`.

## Dependencies And Integration Points
It is tightly coupled to Clang's KMSAN ABI, `struct kmsan_context_state`, shadow/origin address mapping from `shadow.c`, core metadata routines, user access helpers, raw `__memcpy`/`__memmove`/`__memset`, and exported symbols needed by instrumented kernel objects.

## Risks
ABI drift with the compiler would break instrumentation silently or at link time. `memset()` cannot propagate metadata from the fill byte because Clang does not pass that parameter metadata here, so the destination is treated as initialized. Assembly-store size is capped to avoid extreme metadata writes, which can lose precision for unusual asm outputs. Runtime guards are required because origin creation can allocate.

## Test Signals
The KUnit suite validates compiler instrumentation through stack variables, function parameter propagation, printk argument checking, memory intrinsic behavior, memset16/32/64, long origin chains, and local-origin report formatting. Link-time availability of all exported `__msan_*` symbols is a build signal.
