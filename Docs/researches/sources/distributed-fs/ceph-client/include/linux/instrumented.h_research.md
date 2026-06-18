<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instrumented.h -->
# sources/distributed-fs/ceph-client/include/linux/instrumented.h

Purpose: Supplies wrappers around memory and MMIO accesses that notify kernel instrumentation frameworks such as KASAN, KCSAN, and KMSAN.

Important APIs/types/functions: Inline helpers cover reads/writes, reads-before-writes, atomic reads/writes, bit operations, memset/memcpy-style effects, and MMIO variants, usually calling sanitizer hooks before or after real access depending on configuration.

Control flow: Low-level primitives include these wrappers so dynamic analyzers observe memory access semantics while production builds compile away inactive hooks.

State/persistence: No direct state; sanitizer runtimes maintain shadow state externally.

Dependencies/integration: Depends on compiler instrumentation, sanitizer headers, atomic/bitop implementations, and MMIO access code.

Risks: Missing instrumentation hides data races or invalid memory use; instrumenting truly noinstr paths can be unsafe.

Test signals: KASAN/KCSAN/KMSAN builds, race/use-after-free test modules, atomic bitop instrumentation, and MMIO access smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instrumented.h -->
