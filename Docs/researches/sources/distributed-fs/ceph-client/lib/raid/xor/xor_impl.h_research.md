# sources/distributed-fs/ceph-client/lib/raid/xor/xor_impl.h

Purpose: defines the common template ABI and wrapper macros for XOR implementations.

Important APIs and flow: `struct xor_block_template` carries linked-list pointer, name, measured speed, and `xor_gen` function pointer. `__DO_XOR_BLOCKS()` creates a public generator that consumes any `src_cnt` by chunking sources into groups of up to four and dispatching to 2 through 5-buffer handlers, where the destination is counted as the first operand. `DO_XOR_BLOCKS()` makes the generator static. It declares generic templates and registration functions.

State and persistence: the struct carries mutable `speed` and `next` fields during init/calibration.

Dependencies and integration: included by every XOR implementation and `xor-core.c`.

Risks and test signals: macro dispatch must preserve source ordering and handle source counts greater than four. KUnit randomized source counts up to 64 directly exercise this behavior.
