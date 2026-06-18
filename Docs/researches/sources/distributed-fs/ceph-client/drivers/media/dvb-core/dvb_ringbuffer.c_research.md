# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_ringbuffer.c

## Purpose

`dvb_ringbuffer.c` provides the generic circular buffer and packet-record helpers used by DVB core components. It supports byte-stream reads/writes, user-copy variants, flush/reset operations, waitqueue wakeups, and packetized records with a small header containing length and ready/disposed state. In this subset, CA EN50221 uses the packet helpers to queue CAM link fragments.

## Important APIs, Types, And Functions

The exported API includes `dvb_ringbuffer_init`, `dvb_ringbuffer_empty`, `dvb_ringbuffer_free`, `dvb_ringbuffer_avail`, `dvb_ringbuffer_flush`, `dvb_ringbuffer_reset`, `dvb_ringbuffer_flush_spinlock_wakeup`, `dvb_ringbuffer_read_user`, `dvb_ringbuffer_read`, `dvb_ringbuffer_write`, and `dvb_ringbuffer_write_user`. Packet helpers in this file include `dvb_ringbuffer_pkt_write`, `dvb_ringbuffer_pkt_read_user`, `dvb_ringbuffer_pkt_read`, `dvb_ringbuffer_pkt_dispose`, and `dvb_ringbuffer_pkt_next`.

The packet format is `len_hi`, `len_lo`, `status`, followed by payload. Status is `PKT_READY` or `PKT_DISPOSED`. Disposed packets are lazily reclaimed only from the read pointer forward, preserving later packets until all earlier packets are disposable.

## Control Flow

Initialization sets read/write positions to zero, stores caller-provided backing storage and size, clears error state, and initializes the wait queue and spinlock. Free/available calculations use circular pointer arithmetic with one byte reserved to distinguish full from empty.

Read and write operations handle wraparound in two phases. If the requested transfer crosses the end of the backing array, they copy the split tail first, publish the pointer as zero, then copy the remaining head bytes and publish the final modulo position. User variants use `copy_to_user`/`copy_from_user`.

Packet write emits the three-byte header using ring macros, writes the payload, and rolls back `pwrite` if the payload write fails. Packet reads inspect packet length at an arbitrary packet index, clamp reads to the packet length, skip the packet header plus caller offset, and copy across wraparound if needed. Packet dispose marks an arbitrary packet disposed, then advances the read pointer over consecutive disposed packets at the front. Packet next walks from either `pread` or a supplied packet index until it finds a ready packet or runs out of available bytes.

## State And Persistence Behavior

The buffer state is in caller-owned `struct dvb_ringbuffer` and caller-provided data storage. There is no allocation or persistence in this file. The `queue` waitqueue is initialized here but only signaled by `dvb_ringbuffer_flush_spinlock_wakeup`; most users perform their own wakeups.

Memory ordering is explicitly documented. Writer pointer publication uses `smp_store_release`; reader-side availability/empty checks use `smp_load_acquire`; writer-side free checks use `READ_ONCE` on `pread`. This makes single-reader/single-writer style usage safer across CPUs, but callers still need external locking for multi-writer or multi-reader cases and for packet-level compound operations.

## Dependencies And Integration Points

The file depends on kernel wait queues, spinlocks, string copy helpers, and user access helpers. It exposes symbols to the rest of DVB core and adapter drivers. Packet macros and `DVB_RINGBUFFER_PKTHDRSIZE` come from `media/dvb_ringbuffer.h`.

The main integration point in this work item is `dvb_ca_en50221.c`, where CAM link fragments are packet-written by the monitor thread and packet-read/disposed by userspace read paths.

## Risks And Edge Cases

Callers must check available/free space before writing; `dvb_ringbuffer_write` itself does not enforce capacity. Packet helpers assume the header and packet fit and can leave partial header state if misused. `dvb_ringbuffer_pkt_write` only rolls back on negative payload write status, while normal `dvb_ringbuffer_write` currently returns the requested length.

User-copy write returns `len - todo` on copy failure, but during the second copy `todo` has not been reduced yet, so partial-copy semantics need careful testing. Packet indices are `size_t`, but `dvb_ringbuffer_pkt_next` uses `idx == -1` as the sentinel; this relies on unsigned wrap to `SIZE_MAX` and matching caller convention.

External synchronization is still required around compound operations such as scanning packets and disposing selected records. Packet disposal marks status without a barrier or lock in this file; correctness depends on caller locking or single-consumer assumptions.

## Test Signals

Tests should cover empty/free/avail across initial, wrapped, full-minus-one, flush, and reset states; byte reads/writes that split at the end; user-copy fault behavior; packet write/read/read_user for wrapped headers and wrapped payloads; disposing out-of-order packets and verifying only front-disposed packets are reclaimed; `pkt_next` iteration across ready and disposed records; and concurrent producer/consumer stress under the locking model used by each caller.
