# sources/distributed-fs/ceph-client/arch/microblaze/lib/Makefile

Purpose: selects MicroBlaze architecture library objects for string routines, user copy, and libgcc-style arithmetic helpers.

Important build rules and state: removes `-pg` from 64-bit shift helper objects under function tracing, always builds `memset.o`, selects `fastcopy.o` when `CONFIG_OPT_LIB_ASM=y` or C `memcpy.o memmove.o` otherwise, always builds `uaccess_old.o`, and links arithmetic helper objects through `obj-y`.

Control flow: build-time only.

State and persistence: controls which symbols become part of the kernel image and available for module exports.

Dependencies and integration: paired with `microblaze_ksyms.c`, compiler-emitted libgcc calls, and optimized string Kconfig.

Risks and test signals: profiling arithmetic helpers can recurse through ftrace, hence `CFLAGS_REMOVE`. Test build matrix for function tracer and optimized assembly/C libraries, plus module symbol availability.
