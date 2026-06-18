# sources/distributed-fs/ceph-client/arch/arm64/kernel/kaslr.c

Purpose: Publishes whether runtime arm64 KASLR is enabled after early PI mapping has selected any offset.

Important APIs and state: `__kaslr_is_enabled` is `__ro_after_init`. `kaslr_init()` evaluates command-line disablement and `kaslr_offset()`. `parse_nokaslr()` exists only so early cpufeature parsing can own the real `nokaslr` handling.

Control flow: if `nokaslr` was parsed, log disabled. If the offset is less than `MIN_KIMG_ALIGN`, treat it as lacking a seed and disable. Otherwise log enabled and set `__kaslr_is_enabled = true`.

Dependencies and integration: depends on early PI KASLR seed handling in `pi/kaslr_early.c`, feature override command-line parsing, and memory layout helpers. Consumers use the exported state to decide whether the kernel image was randomized.

Risks and test signals: risks are false positives when physical placement contributes low offset bits, mismatched early/late command-line interpretation, or misleading logs. Test with `nokaslr`, missing seed, FDT seed, RNDR seed, and KASLR offset inspection in boot logs.
