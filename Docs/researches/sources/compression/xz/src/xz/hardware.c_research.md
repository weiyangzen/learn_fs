# Research: sources/compression/xz/src/xz/hardware.c
## sources/compression/xz/src/xz/hardware.c

Purpose: Detects hardware resources and manages thread and memory-limit policy for compression, decompression, and threaded decompression.

Important APIs and functions: `hardware_init()` sets `total_ram`, default threaded memory limit, resource-limit caps, 32-bit ceilings, and default automatic thread mode. `hardware_threads_set()`, `hardware_threads_get()`, and `hardware_threads_is_mt()` manage explicit, automatic, and `-T+1` multi-thread mode. `hardware_memlimit_set()` applies byte or percentage limits to compression, decompression, and threaded decompression. `hardware_memlimit_get()`, `hardware_memlimit_mtenc_get()`, `hardware_memlimit_mtenc_is_default()`, and `hardware_memlimit_mtdec_get()` expose hard and soft limits. `hardware_memlimit_show()` prints human or robot memory information and exits.

Control flow: `main.c` calls `hardware_init()` before `args_parse()`. `args.c` updates limits and thread count while parsing. `coder.c` queries limits and thread mode while validating settings and initializing threaded encoders/decoders. `--info-memory` exits through `hardware_memlimit_show()`.

State and persistence: Static state includes `threads_max`, whether thread count was automatic, whether to use threaded mode with one thread, compression/decompression/threaded-decompression limits, default threaded limit, and total RAM. There is no external persistence.

Dependencies and integration points: Uses liblzma CPU/RAM detection, optional `getrlimit()`, gettext/message helpers, `opt_robot`, and `opt_mode`. It provides the policy that lets automatic `-T0` reduce threads without failing simply because the default soft limit is too low.

Risks: Resource-limit margin is heuristic. Percentage limits on 32-bit systems need caps to avoid address-space exhaustion. The distinction between hard decompression limit and soft threaded-decompression limit is subtle and must remain aligned with `coder.c` use of `memlimit_stop` and `memlimit_threading`.

Test signals: Run with `-T0`, `-T1`, `-T+1`, explicit memlimits, percentage memlimits, `--info-memory` robot/human, artificial `RLIMIT_AS`/`RLIMIT_DATA`, 32-bit builds, and builds without threading.
