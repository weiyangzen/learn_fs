<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.c

### Purpose
`unaligned.c` emulates supported unaligned PA-RISC load/store instructions or signals/fixes up failures.

### Important APIs, Types, And Functions
Public state and functions are `unaligned_enabled`, `no_unaligned_warning`, `handle_unaligned()`, and `check_unaligned()`. Internal helpers emulate halfword, word, doubleword, and floating load/store forms.

### Control Flow
The handler counts and reports alignment faults, honors per-thread user alignment-control flags, optionally rejects user unaligned access, decodes the trapped instruction to determine base modification and operation type, emulates memory access using space-register-aware inline assembly with exception table fixups, updates base registers for modifying forms, and nullifies the trapped instruction on success. Failures either use kernel exception fixups, send SIGSEGV/SIGBUS, or call `die_if_kernel()`.

### State, Persistence, And Dependencies
Global policy flags and per-thread flags control warnings and SIGBUS behavior. Dependencies include `pt_regs`, PA-RISC instruction encoding, exception table macros, perf alignment fault events, user access fault handling, and trap code.

### Integration Points
Called from `traps.c` for unaligned data reference traps and PCXS access-rights checks.

### Risks
Instruction decoding is complex and architecture-specific. 64-bit integer doubleword emulation is unavailable on 32-bit builds except FP paths. Emulation must preserve memory ordering and avoid sleeping in fault-sensitive contexts.

### Test Signals
User and kernel unaligned half/word/doubleword, FP load/store, modifying loads/stores, disabled unaligned policy, exception-table fixups, and ratelimited warnings should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.c -->
