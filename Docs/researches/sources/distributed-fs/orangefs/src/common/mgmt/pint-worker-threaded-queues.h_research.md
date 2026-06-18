<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-threaded-queues.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-threaded-queues.h

Purpose: declares the threaded queue worker attributes, thread-entry state, worker state, and exported implementation vtable.

Important types: `PINT_worker_threaded_queues_attr_t` includes `thread_count`, `ops_per_queue`, and queue wait `timeout`. `struct PINT_worker_thread_entry` stores a thread id, back-pointer to the worker, mutex, running flag, and error. `struct PINT_worker_threaded_queues_s` stores attributes, thread array, available and in-use queue lists, mutex/condition, manager pointer, and `remove_requested` coordination flag.

Control flow: the C file starts `thread_count` threads at init; each thread cycles queues and services posted operations. Queue removal uses `remove_requested` and condition broadcasts to avoid removing a queue while a thread is using it.

State behavior is volatile and thread-shared. Attached queues are external objects; the worker references them through intrusive queue links and producer/consumer refs. No persistent state exists.

Dependencies include `gen-locks`, `quicklist`, `pint-op`, pthread-compatible `gen_thread_t`, and the worker vtable contract.

Risks: correctness depends on strict ownership of `struct PINT_queue_s.link` between `queues` and `inuse_queues`. Invalid attributes such as zero threads or zero `ops_per_queue` are not guarded in the header. Tests should include lifecycle with multiple queues and threads, queue removal while active, cancellation, and shutdown with empty queues and pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-threaded-queues.h -->
