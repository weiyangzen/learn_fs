# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kgdb.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kgdb.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kgdb.h

### Purpose
`kgdb.h` defines ARM64 KGDB breakpoint, single-step, fault, and register-packet layout support for kernel remote debugging.

### Important APIs, Types, And Functions
It exports `arch_kgdb_breakpoint()`, `kgdb_handle_bus_error()`, `kgdb_fault_expected`, `kgdb_brk_handler()`, `kgdb_compiled_brk_handler()`, `kgdb_single_step_handler()`, register counts (`_GP_REGS`, `_FP_REGS`, `_EXTRA_REGS`), `DBG_MAX_REG_NUM`, `BUFMAX`, and `NUMREGBYTES`.

### Control Flow
Debug break instructions trap into KGDB handlers. Optional software single-step support routes debug exceptions to `kgdb_single_step_handler()`. Register transfer sizes define how CPU and FP state are serialized to the remote protocol.

### State, Persistence, And Dependencies
The only declared mutable state is `kgdb_fault_expected`; runtime state lives in `pt_regs`, debug monitor state, and KGDB core buffers. It includes `linux/ptrace.h` and `asm/debug-monitors.h`.

### Integration Points
KGDB core, exception handlers, debug monitor code, and architecture register serializers depend on this contract. It helps debug kernel faults that can include Ceph client paths.

### Risks
Register layout drift breaks remote debugging. Incorrect breakpoint encoding or single-step behavior can recurse in exception context. Fault expectation handling must not hide real faults.

### Test Signals
Build and boot with KGDB; connect gdb, set breakpoints, single-step, inspect general/FP registers; test bus-error recovery and compiled breakpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kgdb.h -->
