# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx.c

Purpose: detects Intel TDX in the compressed boot path and replaces raw port I/O callbacks with TDVMCALL-based I/O helpers.

Important APIs and state: exports `early_tdx_detect()` and `__tdx_hypercall_failed()`. It defines `tdx_io_in()`, `tdx_io_out()`, and byte/word wrappers used to populate `pio_ops`. State is external via `pio_ops` from real-mode/compressed I/O support.

Control flow: `early_tdx_detect()` issues CPUID leaf `TDX_CPUID_LEAF_ID` and compares the returned vendor signature with `TDX_IDENT`. On match, it sets `pio_ops.f_inb`, `f_outb`, and `f_outw` to TDX hypercall wrappers. The wrappers fill `struct tdx_module_args` for `EXIT_REASON_IO_INSTRUCTION`, with direction, port, width, and value encoded in registers, then call `__tdx_hypercall()`.

Dependencies and integration: depends on boot `cpuflags.h`, `io.h`, shared TDX definitions, and the common TDX hypercall assembly. It is called early enough that subsequent setup console/BIOS-style port I/O can be virtualized correctly in a TDX guest.

Risks and test signals: if detection runs late, raw I/O instructions may #VE or fail in TDX. `tdx_io_in()` returns `UINT_MAX` on hypercall failure, which consumers must tolerate. Test with TDX and non-TDX boots, early serial/console paths, and failure injection for TDVMCALL to ensure `error()` is reached for unrecoverable failures.
