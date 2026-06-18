# sources/distributed-fs/ceph/src/librados/librados_asio.h

## Purpose

`librados_asio.h` adapts librados asynchronous object/watch/notify operations to Boost.Asio's asynchronous operation model. It lets callers use completion tokens, associated executors, and cancellation slots while internally driving regular librados `AioCompletion` callbacks.

## Important APIs, Types, and Functions

Important detail types are `AioCompletionDeleter`, `unique_aio_completion_ptr`, `Invoker<Result>` and its `void` specialization, `AsyncHandler<Handler>`, and `AsyncOp<Result>`. `AsyncOp` owns the `AioCompletion`, registers `aio_dispatch()` as the librados callback, extracts return value and object version directly from `AioCompletionImpl`, converts negative errno to `boost::system::error_code`, and dispatches the user handler. `op_cancellation` maps Asio cancellation to `AioCompletion::cancel()`, allowing all cancellation types for reads and only terminal cancellation for writes.

Public templates include `async_read()`, `async_write()`, read and write overloads of `async_operate()`, `async_watch()`, `async_unwatch()`, and `async_notify()`. They all use `boost::asio::async_initiate`, create an `AsyncOp`, call the matching `IoCtx::aio_*` method, post immediate errors, and release completion ownership until callback.

## Control Flow and Data Flow

The user calls an `async_*` helper with an executor, `IoCtx`, operation arguments, and completion token. The initiating lambda creates a Ceph async `Completion` carrying the wrapped handler and an owned librados `AioCompletion`. On successful submission, ownership is released to the librados callback. On completion, `aio_dispatch()` reclaims the `Completion`, moves result storage out, reads `rval` and `objver`, creates an error code when needed, and dispatches the handler with `(error_code, version_t[, result])`. `AsyncHandler` clears the cancellation slot before destroying the `AioCompletion`, preventing a cancellation handler from referencing a freed completion.

## State and Persistence Behavior

The file manages transient async state only. Persistent RADOS effects are those of the submitted write, operate, watch, unwatch, or notify operation. Result-bearing operations store a `bufferlist` until handler dispatch. Object version is returned as local completion metadata.

## Dependencies and Integration Points

It depends on Boost.Asio cancellation/associator/executor support, public librados C++ API, Ceph async completion utilities, and `AioCompletionImpl`. It integrates with `IoCtx` async methods and can be used by applications that already run Boost.Asio event loops.

## Risks and Edge Cases

The template signatures include a `trace_ctx` parameter for `async_operate()` read overload but the initiating lambda does not forward it; write operate does forward it. The comments say an `IoCtx` reference need not remain valid, but some `IoCtx` instance must keep the underlying implementation alive, so applications can still create lifetime bugs. Direct access to `AioCompletionImpl` avoids locking and assumes callback-time stability. Cancellation semantics differ for read and write because writes may already have side effects.

## Test Signals

Tests should use callback, future, coroutine, and custom token styles; verify executor association; confirm immediate submission errors are posted; check version and error-code mapping; test read bufferlist results; exercise cancellation before and after submission; verify write cancellation only responds to terminal cancellation; and run lifetime tests where the initiating `IoCtx` wrapper is destroyed while another reference keeps the implementation alive.
