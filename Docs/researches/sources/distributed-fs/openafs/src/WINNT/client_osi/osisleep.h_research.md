<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.h

Purpose: Declares sleep-info state, turnstile structures, once-control structure, hash constants, sleep/wakeup APIs, sleep fd APIs, panic/time utilities, and assertion macros for the OSI layer.

Important APIs, types, and functions: `osi_sleepInfo_t` stores queue linkage, sleep value, thread id, semaphore, states, bucket index, wait reason, and fd refcount. `osi_turnstile_t` stores first/last sleeper pointers. `osi_sleepFD_t` is the remote-debug cursor. `osi_once_t` has `atomic` and `done`. State bits include signalled, in-hash, deleted, wait-for-read, and wait-for-write. Hash constants are `OSI_MUTEXHASHSIZE`, `OSI_SLEEPHASHSIZE`, `osi_MUTEXHASH`, and `osi_SLEEPHASH`. Public functions include sleep/wakeup, init, sleep info free, once helpers, sleep cookie declarations, fd ops, prime helpers, boot time, panic, time, turnstile waits/signals, and `osi_TInit` / `osi_TEmpty`.

Control flow and state: Callers initialize OSI, then sleep on integer/pointer values or use turnstiles from lock code. Assertions call `osi_panic` with file and line.

Persistence and dependencies: No persistence. Depends on fd and queue headers and OSI thread/event types supplied by the aggregate include path.

Integration points: Used by base locks, stats locks, logging, fd registry, and panic handling.

Risks: Some declared sleep cookie functions are not implemented in the read file; callers may rely instead on fd functions. Hash macros assume pointer/integer values can be shifted and moduloed safely. Assertion macros evaluate expressions once but terminate through panic side effects rather than returning errors.

Test signals: Header/API tests should cover compile visibility, hash behavior for representative pointers, assertion/panic wiring, and matching declarations to implementation exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.h -->
