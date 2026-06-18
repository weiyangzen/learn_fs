# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-thread.c

## Purpose

Implements SPL thread compatibility APIs over Linux kthreads. It supplies Solaris-style `thread_create()` behavior, an OpenZFS-specific resilient kthread creation wrapper, signal handling compatibility, and a reclaim-thread predicate.

## Key Components

- `thread_priv_t`: temporary launch structure carrying function, argument, name, start state, priority, and magic validation.
- `thread_generic_wrapper()`: unwraps `thread_priv_t`, applies task state and priority, frees launch metadata, then calls the requested function.
- `__thread_create()`: allocates launch metadata, strips a trailing `_thread` substring from the generated name, creates a Linux kthread with `spl_kthread_create()`, wakes it, and returns the task pointer.
- `spl_kthread_create()`: repeatedly calls `kthread_create()` and retries on pending signals or `-ENOMEM`, approximating older non-killable creation semantics.
- `issig()`: Solaris-like pending-signal check that handles Linux `dequeue_signal()` API variants, stop signals, and pending status.
- `current_is_reclaim_thread()`: returns whether the current task is `kswapd`.

## Exports

- `__thread_create`
- `spl_kthread_create`
- `issig`
- `current_is_reclaim_thread`

## Notes

`__thread_create()` ignores the Solaris `proc_t *pp` argument and does not support caller-provided stacks. The file intentionally favors blocking/retry behavior because many Solaris-style callers do not expect thread creation failure.
