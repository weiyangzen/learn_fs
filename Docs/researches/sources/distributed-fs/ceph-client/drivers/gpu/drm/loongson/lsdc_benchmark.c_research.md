# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_benchmark.c

Purpose: debugfs benchmark helper for CPU copy throughput between Loongson GTT and VRAM buffer objects.

Important APIs/types/functions: copy helpers for GTT-to-VRAM, VRAM-to-GTT, GTT-to-GTT, `lsdc_benchmark_copy`, and exported `lsdc_show_benchmark_copy`.

Control flow: the debugfs entry allocates two kernel-pinned BOs in selected domains, maps both, copies a 1920x1080x4 buffer 60 times with the appropriate memcpy variant, measures jiffies elapsed, frees BOs, and prints throughput.

State and persistence: temporary pinned BOs are allocated and freed per benchmark invocation. No persistent state except debug output.

Dependencies and integration points: depends on TTM BO helpers, `lsdc_domain_to_str`, DRM printer, and debugfs caller in `lsdc_debugfs.c`.

Risks and test signals: time can be zero for very fast paths, risking divide-by-zero. Benchmark pins significant memory and should not run on low-memory systems. Test debugfs benchmark on VRAM/GTT paths and cleanup after errors.
