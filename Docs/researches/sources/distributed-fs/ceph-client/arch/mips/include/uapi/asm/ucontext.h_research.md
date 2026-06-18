<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ucontext.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ucontext.h

### Purpose
`ucontext.h` defines the MIPS userspace signal context container and an extensible trailer for processor state that does not fit inside `sigcontext`, notably MSA vector state.

### Important APIs, Types, And Functions
It exports `struct extcontext`, `struct msa_extcontext`, `MSA_EXTCONTEXT_MAGIC`, `END_EXTCONTEXT_MAGIC`, and `struct ucontext` with `uc_flags`, `uc_link`, `uc_stack`, `uc_mcontext`, `uc_sigmask`, and flexible `uc_extcontext[]`.

### Control Flow
There is no executable logic. Userland walks the extension area by reading each `extcontext.magic` and `extcontext.size` until the end magic is seen.

### State, Persistence, And Dependencies
The state is the signal-frame ABI persisted on user stacks during signal delivery. It depends on `stack_t`, `struct sigcontext`, and `sigset_t` declarations from surrounding UAPI headers.

### Integration Points
Signal delivery/return, context-switching libraries, debuggers, crash dump tools, and MSA-aware runtimes parse this layout.

### Risks
Extension parsing depends on size correctness, alignment, and the end marker. Unknown extensions must be skippable, so future additions must preserve this contract.

### Test Signals
Signal tests should inspect `ucontext_t`, MSA live-state delivery, unknown-extension skipping, end-marker placement, and ABI layout under O32, N32, and N64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ucontext.h -->
