<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_buffer_fill.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_buffer_fill.c

Purpose: MTE memory correctness selftest for byte/block writes, underflow/overflow behavior, tag-check modes, and initial tag state.

Important APIs and functions: uses shared helpers `mte_default_setup`, `mte_switch_mode`, `mte_allocate_memory`, `mte_allocate_memory_tag_range`, `mte_insert_tags`, `mte_wait_after_trig`, `mte_free_*`, and current fault context. Core tests are `check_buffer_by_byte`, `check_buffer_underflow_by_byte`, `check_buffer_overflow_by_byte`, `check_buffer_by_block_iterate`, `check_buffer_by_block`, `compare_memory_tags`, and `check_memory_initial_tags`.

Control flow: main fills size table with page-size boundary cases, sets up MTE and SIGSEGV handling, plans 20 tests, then evaluates sync/async/no-error modes across mmap and mprotect allocations. Underflow/overflow tests validate precise vs imprecise fault timing and whether neighboring bytes were modified.

State and persistence: allocates and frees anonymous/file mappings; creates temporary files through shared utilities for file mmap initial-tag checks. Uses global `cur_mte_cxt` fault state.

Dependencies and integration: depends on `mte_common_util.h`, `mte_def.h`, kselftest, MTE-capable kernel/hardware, and signal handlers.

Risks: async fault timing is inherently imprecise, so checks must allow writes before fault. Size calculations around unaligned allocation lengths and granule alignment are sensitive.

Test signals: 20 kselftest evaluations; diagnostics identify buffer index, tag mismatch, or unexpected fault behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_buffer_fill.c -->
