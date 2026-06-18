# sources/distributed-fs/ceph/src/osd/Coroutines.h

## Purpose
`Coroutines.h` defines the minimal coroutine handle types used to integrate Boost.Coroutine2 with OSD backend code, especially synchronous-looking wrappers around asynchronous EC reads.

## Important APIs, Types, and Control Flow
The file aliases `yield_token_t` to `boost::coroutines2::coroutine<void>::pull_type` and `resume_token_t` to `push_type`. `CoroHandles` groups references to a yield and resume handle so a caller can yield while an async operation is outstanding and resume from its completion callback.

## State and Persistence Behavior
There is no persistent state and no ownership. `CoroHandles` contains references, so lifetime is entirely controlled by the caller/coroutine frame. Misuse after the coroutine frame exits would be unsafe.

## Dependencies and Integration Points
It depends only on Boost.Coroutine2. `ECBackend::objects_read_sync()` uses `CoroHandles` to call `objects_read_async()`, yield if the read has not completed, and resume when the callback fires.

## Risks and Test Signals
Risks include dangling handle references, double resume, completion before the caller marks itself waiting, and exceptions or cancellation paths that skip resume. Tests should exercise immediate completion, delayed completion, error completion, and cancellation/destruction of async contexts while a coroutine wrapper is waiting.
