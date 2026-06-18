# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/misc.c



Source read size: 141 lines, 2710 bytes.



Purpose: minimal C decompressor runtime for SH zImage, including tiny libc routines, stack protector hooks, ftrace stubs, heap setup, and selected compression backends.

Important APIs/types/functions: `decompress_kernel()`, `puts()`, local `memset()`/`memcpy()`, `error()`, `__stack_chk_guard`, `__stack_chk_fail()`, `ftrace_stub()`, `arch_ftrace_ops_list_func()`, `input_data`, `input_len`, and `__decompress()`.

Control flow: `decompress_kernel()` computes the output address at `_text + PAGE_SIZE`, applies P2 segment mapping for 29-bit mode, sets a small or bzip2-sized heap after `_end`, invokes the selected decompressor, and returns to assembly to jump into the kernel.

State and persistence: owns transient boot heap pointers, output pointer, and bootstrap stack array; on error it loops forever after optional messages.

Dependencies and integration points: includes decompressor source files directly from `lib/`, uses `__pa`, segment helpers, linker symbols, and is called by `head_32.S`/`head_64.S`.

Risks and test signals: no real console output is implemented; heap sizing must satisfy decompressor requirements; wrong 29-bit address conversion corrupts output. Test every compression algorithm, stack protector builds, and 29-bit versus full-address configs.
