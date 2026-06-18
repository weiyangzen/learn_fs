## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_task.cpp

Purpose: Implements a simple background task queue with bounded worker thread fan-out and `WM_ENDTASK` completion messages.

Important APIs and functions: `AfsAppLib_InitTaskQueue` installs caller-provided `TASKQUEUE_PARAMS`. `StartTask` enqueues task ID/reply HWND/user data and starts threads up to `nThreadsMax`. `Task_ThreadProc` pops work, creates/performs/frees task packets through callbacks, and posts results.

Control flow: First `StartTask` initializes the critical section. Each task increments active count, may spawn a below-normal-priority worker, then appends to a singly linked FIFO. Worker threads loop: decrement active count from prior work, pop one item, exit if none, call create/perform callbacks, then post `WM_ENDTASK` to the reply window or free the packet directly if no valid window remains.

State and persistence: Global `ptqp`, FIFO head/tail, critical section, `nThreadsRunning`, and `nRequestsActive`. No persistent storage.

Dependencies and integration points: Depends on task callback types from `afsapplib.h`, Win32 threads, and `WM_ENDTASK` from `al_messages.h`. UI receivers must free task packets after processing `WM_ENDTASK`.

Risks: Thread handles are not closed. `AfsAppLib_InitTaskQueue` can replace params while workers still use `ptqp`. No shutdown drain. Active count/thread count logic is compact and sensitive to races if init/reinit occurs concurrently. Posting a packet to a window transfers ownership by convention only.

Test signals: Single and multiple tasks, max-thread limits, reply window destroyed before completion, callback packet creation failure, task queue reinitialization, and receiver packet-free handling.
