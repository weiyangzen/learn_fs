<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/ftrace_regs.h

Purpose: Defines the default architecture wrapper and accessor expectations for `struct ftrace_regs`, the register snapshot abstraction passed to ftrace callbacks.

Important APIs/types/functions: Without `HAVE_ARCH_FTRACE_REGS`, `struct __arch_ftrace_regs` wraps `struct pt_regs`; `arch_ftrace_regs()` casts from `ftrace_regs`. Default accessors expose instruction pointer, arguments, stack pointer, return value, return override, register offset query, and frame pointer. `ftrace_partial_regs_update()` synchronizes changed partial register views. `FTRACE_REGS_MAX_ARGS` defaults to six.

Control flow: Ftrace callbacks use accessor macros rather than touching architecture storage. If an architecture has custom ftrace register layout, it defines `HAVE_ARCH_FTRACE_REGS` and supplies equivalent accessors; otherwise these defaults route through generic `pt_regs` helpers.

State and persistence behavior: No independent state is stored. The header defines how an existing per-callback register snapshot is interpreted and optionally updated.

Dependencies and integration points: Depends on architecture `pt_regs` helpers such as `instruction_pointer()`, `regs_get_kernel_argument()`, `kernel_stack_pointer()`, and return override helpers. Integrated directly by `ftrace.h`.

Risks: Incorrect architecture accessor definitions can corrupt function arguments, return values, or instruction pointer changes used by live patching and tracing. Partial register updates are subtle on architectures that copy rather than embed `pt_regs`.

Test signals: Architecture ftrace regs selftests, callbacks that inspect arguments and modify return values, livepatch/fprobe tests, and compile coverage with and without custom arch ftrace regs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace_regs.h -->
