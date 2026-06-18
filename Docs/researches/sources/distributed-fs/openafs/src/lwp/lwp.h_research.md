# sources/distributed-fs/openafs/src/lwp/lwp.h

Purpose: public LWP and IOMGR interface header for non-kernel OpenAFS builds. It defines the cooperative lightweight process ABI when `AFS_PTHREAD_ENV` is not active and exposes fasttime, LWP scheduler, IOMGR select/sleep, and keyboard wait helpers.

Important APIs/types/functions: `PROCESS` is a pointer to `struct lwp_pcb`. The Unix PCB stores name, status, block flag, event list, wait counts, priority, stack memory, saved `lwp_context`, per-process rocks, IOMGR request pointer, and an index. The NT PCB uses a Windows fiber and a smaller state set. Public calls include `LWP_InitializeProcessSupport`, `LWP_CreateProcess`, `LWP_DestroyProcess`, `LWP_WaitProcess`, `LWP_INTERNALSIGNAL`, `LWP_QWait`, `LWP_QSignal`, `LWP_DispatchProcess`, `LWP_TerminateProcessSupport`, `LWP_CurrentProcess`, `LWP_ThreadId`, `savecontext`, and `returnto`. IOMGR entry points allocate fd sets and wrap select/poll/sleep/cancel.

Control flow: callers initialize LWP support, create runnable PCBs, wait on event addresses, signal events, and voluntarily dispatch. Context switching is delegated to platform C or assembly implementations declared here. The header also maps `LWP_SignalProcess` and `LWP_NoYieldSignal` to `LWP_INTERNALSIGNAL` on most platforms.

State and persistence: all state is process-memory only. Global `lwp_cpptr`, `lwp_debug`, stack sizing variables, overflow action, and `lwp_nextindex` are shared scheduler state. There is no disk persistence.

Dependencies/integration: depends on `afs/param.h`, platform select headers, `ucontext` or `setjmp`, Windows headers under NT, and LWP implementation files. It is consumed by LWP tests, IOMGR, lock tests, and legacy server code.

Risks and test signals: ABI and structure layout are architecture-sensitive, especially `lwp_context` and `lwp_pcb`. Stack-size constants encode historical platform behavior. Tests in `src/lwp/test` exercise process switching, event signaling, IOMGR select, and keyboard helpers.
