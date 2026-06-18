# sources/distributed-fs/openafs/src/rx/rx_pthread.c

## Purpose
Implements pthread-based RX thread support: listener threads, server-thread startup, event scheduling thread, `recvmsg`/`sendmsg` wrappers, per-thread RX identifiers, and listener/server role handoff for hot threads.

## Important APIs, Types, And Functions
Key functions include `rx_NewThreadId`, `rxi_Delay`, `rxi_InitializeThreadSupport`, `rxi_StartServerProc`, `rxi_ReScheduleEvents`, `rxi_Listen`, `rxi_StartListener`, `rx_ServerProc`, `rxi_Recvmsg`, `rxi_Sendmsg`, `rx_GetThreadNum`, and `rx_SetThreadNum`. Important local functions are `event_handler`, `server_entry`, `rxi_ListenerProc`, `rx_ListenerProc`, and `rxi_SetThreadNum`. State includes `event_handler_thread`, `rx_event_handler_cond`, `event_handler_mutex`, `rx_listener_cond`, `listener_mutex`, `listeners_started`, `rxi_clockNow`, `threadHiNum`, and `rx_pthread_event_rescheduled`.

## Control Flow
`rxi_Listen` creates a detached listener thread per socket. Listeners block on `rx_listener_cond` until `rxi_StartListener` starts the detached event handler and broadcasts startup. Listener loops allocate/reuse receive packets, call `rxi_ReadPacket`, timestamp successful reads, and pass packets to `rxi_ReceivePacket`. With hot threads, a listener can return with `newcallp` set and become a server thread. `rx_ServerProc` reserves packets/quota, assigns a unique thread ID, calls the core `rxi_ServerProc`, then can become a listener when handed a socket. The event handler repeatedly raises due events and sleeps until the next deadline or `rxi_ReScheduleEvents` signals an earlier event.

## State And Persistence
State is process-local thread and synchronization state. Thread IDs are stored in pthread-specific data using `rx_thread_id_key`. There is no disk persistence. Listener startup is intentionally one-way; comments note `listeners_started` is not reset unless listener termination is implemented.

## Dependencies And Integration Points
This file is compiled under `AFS_PTHREAD_ENV` and depends on `rx_globals.h`, `rx_pthread.h`, `rx_clock.h`, `rx_atomic.h`, `rx_internal.h`, packet receive functions, event functions, and platform `recvmsg`/`sendmsg` or Windows shim functions. It is the pthread implementation behind prototypes shared with LWP and kernel code.

## Risks And Test Signals
Risks include detached-thread creation failures causing panic, listener startup races, hot-thread role handoff mistakes, event reschedule timing bugs, ignored stack-size parameter, and platform-specific send error normalization. Test signals include pthread RX server/client smoke tests, timer/event latency, simultaneous listeners, packet receive under load, send failures returning negative errno values, and thread ID uniqueness.
