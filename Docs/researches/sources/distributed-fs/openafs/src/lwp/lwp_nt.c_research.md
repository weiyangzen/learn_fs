# sources/distributed-fs/openafs/src/lwp/lwp_nt.c

Purpose: Windows NT implementation of the LWP scheduler using Windows fibers. It mirrors the Unix LWP API so the rest of OpenAFS can use one cooperative-process model.

Important APIs/types/functions: exports `LWP_InitializeProcessSupport`, `LWP_CreateProcess`, `LWP_DestroyProcess`, `LWP_QWait`, `LWP_QSignal`, `LWP_CurrentProcess`, `LWP_ThreadId`, `LWP_DispatchProcess`, `LWP_GetProcessPriority`, `LWP_INTERNALSIGNAL`, `LWP_TerminateProcessSupport`, and `LWP_WaitProcess`. Internal helpers include `Initialize_PCB`, `Enter_LWP`, `Dispatcher`, `Internal_Signal`, `purge_dead_pcbs`, `Delete_PCB`, `Free_PCB`, and circular queue operations. `runnable[MAX_PRIORITIES]` and `blocked` hold PCB queues.

Control flow: initialization converts the main thread to a fiber, creates the control block, initializes queues, and inserts the main PCB. New LWPs allocate a PCB, enforce minimum stack size, create a fiber, insert it by priority, then switch to it. Waiting moves the current PCB from runnable to blocked with event-list metadata. Signaling scans blocked PCBs for matching event pointers, decrements wait counts, and moves satisfied PCBs back to runnable. `Dispatcher` advances the current queue head, chooses the highest non-empty priority queue, updates `lwp_cpptr`, and calls `SwitchToFiber`.

State and persistence: process-local globals hold scheduler state, process count, current PCB, queues, stack-size metrics, and debug flags. No persistent storage is used.

Dependencies/integration: compiled only for `AFS_NT40_ENV`; uses Windows fiber APIs, `afs/opr.h`, `afs/afsutil.h`, and `lwp.h`. IOMGR uses `lwp_MaxStackSeen` and PCB `iomgrRequest` fields.

Risks and test signals: the Win95 compatibility stubs return null/no-op and would not provide real scheduling. `LWP_CreateProcess` switches to the new fiber before assigning `*pid`, which preserves old LWP behavior but makes caller assumptions delicate. Queue corruption and destroyed-PCB lifetime are main risks. LWP tests cover analogous API behavior but Windows-specific fiber paths need platform build/runtime testing.
