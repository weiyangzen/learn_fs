# Research: sources/compression/xz/src/xz/hardware.h
## sources/compression/xz/src/xz/hardware.h

Purpose: Declares the hardware resource and memory-limit interface.

Important APIs: Exposes initialization, thread setter/getter/multithread predicate, generic memory-limit setter, hard compression/decompression limit getter, threaded encoder default-limit getter/predicate, threaded decompression soft-limit getter, and the noreturn `hardware_memlimit_show()`.

Control flow and integration: `main.c` initializes hardware early; `args.c` mutates it; `coder.c` consumes it; `message.c` indirectly queries it through `message_mem_needed()`.

State and persistence: All state is private to `hardware.c`; consumers only see computed values.

Risks: The API depends on `enum operation_mode` from `coder.h`, so include ordering through `private.h` matters. Misusing `hardware_memlimit_mtdec_get()` as a hard limit would change decoder behavior.

Test signals: Header coverage comes from CLI integration around threads, memlimits, and `--info-memory`.
