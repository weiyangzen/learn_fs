## sources/distributed-fs/ceph-client/arch/x86/entry/thunk.S

Purpose: defines exported assembly thunks that save/prepare registers before entering scheduler functions from sensitive assembly contexts.

Important APIs/functions: `THUNK preempt_schedule_thunk, preempt_schedule` and `THUNK preempt_schedule_notrace_thunk, preempt_schedule_notrace`, both exported. The actual thunk body comes from `calling.h`.

Control flow: callers branch/call into the thunk symbol, which follows the shared x86 thunk convention to protect register allocation assumptions around inline assembly and then calls the target C scheduler routine.

State/persistence: no file-owned persistent state; it preserves transient register state according to the thunk macro and exports symbols for other kernel code.

Integration points: preemption, scheduler, low-level entry/exit assembly, module symbol resolution, and `calling.h`.

Risks: macro semantics must remain compatible with callers that rely on register preservation in nonstandard contexts. Test signals include preemption stress, objtool validation, module symbol checks, and scheduler tracing around `preempt_schedule_notrace`.
