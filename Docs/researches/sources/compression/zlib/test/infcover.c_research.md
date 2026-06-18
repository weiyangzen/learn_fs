# sources/compression/zlib/test/infcover.c

`infcover.c` is a white-box coverage driver for inflate-side code. It includes `zlib.h`, then defines `ZLIB_INTERNAL` to access `inftrees.h`, `inflate.h`, private inflate state, and `inflate_table()`. It crafts byte streams, allocation failures, bad parameters, state mutations, and callback edge cases to cover `inflate.c`, `infback.c`, `inftrees.c`, and `inffast.c`.

The memory harness uses `mem_item` and `mem_zone` plus `mem_alloc()`, `mem_free()`, `mem_setup()`, `mem_limit()`, `mem_used()`, `mem_high()`, and `mem_done()` to track current/high-water allocation, limit allocations, and report leaks or unusual frees. `h2b()` decodes loose hex input. `inf()` is the generic inflate runner; `try()` compares `inflate()` and `inflateBack()` behavior on raw streams.

`main()` calls `cover_support()`, `cover_wrap()`, `cover_back()`, `cover_inflate()`, `cover_trees()`, and `cover_fast()`. State is in-memory only, except that tests intentionally mutate internal inflate modes and `pull()` uses a static index. Dependencies on private structs make this brittle across internal refactors, and compiling with `NDEBUG` would erase the assertions. Success is exit 0 with coverage/progress output; failures are assertion aborts or memory diagnostics.
