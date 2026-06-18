# sources/distributed-fs/openafs/src/lwp/process.c

Purpose: C implementation of LWP context switching for platforms using `ucontext` or manipulable `setjmp` buffers instead of architecture assembly.

Important APIs/types/functions: exports `savecontext` and `returnto`. Under `USE_UCONTEXT && HAVE_UCONTEXT_H`, `savecontext` uses `getcontext`, `makecontext`, and `setcontext`; otherwise it uses `setjmp`, mutates the stack-pointer slot in `jmp_buf`, and returns through `longjmp`. Platform macros define `LWP_SP` and sometimes `LWP_FP`.

Control flow: `savecontext` sets `PRE_Block`, captures current context, stores a top-stack pointer, and either invokes the supplied entry point on the current stack or creates/switches to a new stack. The `setjmp` path uses a temporary jump buffer to install the new stack pointer and then calls the entry function. `returnto` clears `PRE_Block` and restores the saved context via `setcontext` or `longjmp`.

State and persistence: manipulates only process runtime state: saved context buffers, stack pointers, static helper globals (`EP`, `rc`, `jmpBuffer`), and `PRE_Block`. No persistent state.

Dependencies/integration: included by LWP scheduler implementations through `lwp.h`. Depends on `afs/param.h` platform macros, `roken.h`, `assert.h`, libc context APIs, and glibc pointer-mangling details for some old SPARC cases.

Risks and test signals: the `setjmp` path is highly libc- and architecture-dependent. Several Linux architectures are explicitly unsupported unless `LWP_SP` is known. Pointer mangling and frame-pointer updates can break across libc releases. Runtime process-switch tests are essential.
