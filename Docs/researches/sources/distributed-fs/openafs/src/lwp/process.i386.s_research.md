# sources/distributed-fs/openafs/src/lwp/process.i386.s

Purpose: i386 assembly implementation of `savecontext` and `returnto` for LWP stack/context switching.

Important APIs/types/functions: exports `_C_LABEL(savecontext)` and `_C_LABEL(returnto)`. `savecontext` receives `f`, `area1`, and `newsp` at standard i386 stack offsets. The save area stores `topstack` at offset 0.

Control flow: `savecontext` pushes a new frame, executes `pusha` to save registers, sets `PRE_Block`, writes `%esp` into the save area, optionally switches `%esp` to `newsp`, and jumps to the entry function. `returnto` restores `%esp` from the save area, executes `popa`, clears `PRE_Block`, restores `%ebp`, and returns.

State and persistence: only CPU stack/register state and global `PRE_Block` are modified. No file or heap persistence.

Dependencies/integration: includes `lwp_elf.h` for labels. It is consumed by the LWP scheduler on 32-bit x86 builds that use assembly context switching.

Risks and test signals: assumes classic i386 calling convention and `pusha`/`popa` availability. Stack alignment and signal/preemption interactions are sensitive. Behavioral validation comes from LWP process-switch, wait/signal, and IOMGR tests.
