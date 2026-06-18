# Research: sources/distributed-fs/ceph-client/drivers/tty/tty_buffer.c

## Purpose

`tty_buffer.c` implements tty flip-buffer allocation, queuing, flushing, and delivery to tty clients/line disciplines. It provides the producer-side APIs used by drivers to insert received bytes and the consumer-side workqueue path that forwards committed data in order.

## Important APIs, Types, and Functions

The file operates on `struct tty_port` and its `struct tty_bufhead`. Exported APIs include `tty_buffer_lock_exclusive`, `tty_buffer_unlock_exclusive`, `tty_buffer_space_avail`, `tty_buffer_free_all`, `tty_buffer_flush`, `tty_buffer_request_room`, `__tty_insert_flip_string_flags`, `tty_prepare_flip_string`, `tty_ldisc_receive_buf`, `tty_flip_buffer_push`, `tty_buffer_set_limit`, plus internal work controls declared through `tty.h`: `tty_buffer_init`, `tty_buffer_set_lock_subclass`, `tty_buffer_restart_work`, `tty_buffer_cancel_work`, and `tty_buffer_flush_work`.

Key helpers are `tty_buffer_alloc`, `tty_buffer_free`, `__tty_buffer_request_room`, `lookahead_bufs`, `receive_buf`, `flush_to_ldisc`, and `tty_flip_buffer_commit`. Constants define minimum allocation size, 256-byte alignment, default memory limit, and page-friendly chunk sizing.

## Control Flow

Drivers reserve space with `tty_buffer_request_room`, `tty_prepare_flip_string`, or insertion helpers. `__tty_buffer_request_room` either uses space in the current tail buffer or allocates a new aligned buffer, commits the old tail with release ordering, links the new buffer with release ordering, and returns available linear space. Insert helpers copy character data and optional flag data into the tail and advance `used`.

Once a driver has produced data, `tty_flip_buffer_push` commits `tail->used` to `tail->commit` with release ordering and queues `buf.work`. `flush_to_ldisc` runs as the serialized consumer under `buf->lock`: it stops if exclusive priority is active, advances past empty committed buffers, calls the tty client `receive_buf` callback for readable bytes, zeros consumed character data, updates `read`, invokes lookahead when the consumer accepted only part of a buffer, frees fully consumed old buffers, and yields with `cond_resched`.

Flush and teardown paths use `tty_buffer_flush` to discard queued receive data and optionally flush the line discipline, and `tty_buffer_free_all` to release active and free-list buffers when the tty is no longer in use. Exclusive locking increments `priority`, takes the buffer mutex, and later queues work again if unread committed bytes remain.

## State and Persistence Behavior

Buffer state is per tty port. `buf->head` points to the consumer buffer, `buf->tail` to the producer buffer, `sentinel` anchors an empty queue, `free` caches small buffers, `mem_used` tracks allocated buffer payload bytes, `mem_limit` bounds allocation, `priority` blocks worker consumption for exclusive users, and `work` performs deferred delivery. Data persists in memory until delivered, flushed, or freed; no data is persisted outside tty consumers.

Memory ordering is part of the state contract: producers publish `commit` and `next` with `smp_store_release`, while consumers and flush/lookahead paths use acquire loads to see initialized buffer contents and links.

## Dependencies and Integration Points

The code integrates with tty drivers through flip-buffer insertion APIs, tty ports, tty client operations (`receive_buf` and optional `lookahead_buf`), line discipline receive callbacks (`receive_buf`/`receive_buf2`), workqueues, llist free buffers, atomic counters, mutexes, lockdep subclasses, and memory allocation. PTY code uses `tty_insert_flip_string_and_push_buffer` to combine insertion and push under `port->lock`.

## Risks and Edge Cases

The effective memory use can exceed `mem_limit` because buffers store both data and flags and allocation is checked before a new buffer is added. Producers can still fail allocation in atomic context; callers must handle short insertion. Partial line-discipline consumption triggers lookahead and leaves data queued, so receive callbacks must make forward progress or work will repeatedly stop. Exclusive access relies on balanced priority increments/decrements. Incorrect release/acquire ordering would risk consumers observing uninitialized data or broken buffer links.

## Test Signals

Important tests include high-rate driver insertion, allocation failure and memory-limit behavior, flagless-to-flagged buffer transitions, partial `receive_buf2` consumption, lookahead callbacks, exclusive lock/unlock with pending bytes, flush during concurrent producer activity, work cancellation/restart, small-buffer free-list reuse, `tty_buffer_set_limit` validation, and lockdep coverage for slave pty subclassing.
