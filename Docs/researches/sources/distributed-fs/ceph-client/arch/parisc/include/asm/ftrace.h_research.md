# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ftrace.h

Purpose: defines PA-RISC ftrace integration points and call-site patching constraints.

Important APIs/types/functions: declares `MCOUNT_INSN_SIZE`, graph tracing support, `return_address`/ftrace frame details, and architecture hooks used by dynamic ftrace.

Control flow: ftrace records call sites, patches branch/call instructions through text-patching code, and optionally redirects returns for function graph tracing.

State and persistence: patched text and tracing metadata persist until tracing is disabled or repatched. Dependencies and integration: depends on text patching, unwinding, module loading, and compiler instrumentation.

Risks and test signals: bad instruction-size or return-address assumptions crash traced functions. Test with function and graph tracing, module tracepoints, and objdump validation of patched call sites.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
