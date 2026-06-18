# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_demux.c

## Purpose

`dvb_demux.c` implements the in-kernel DVB demux core. It manages demux users, frontends, TS feeds, section feeds, software TS packet filtering, section reconstruction, section filter matching, CRC checking, PES PID tracking, and memory-fronted demux writes. Adapter demux drivers embed `struct dvb_demux`, supply optional `start_feed`, `stop_feed`, `write_to_decoder`, `check_crc32`, and `memcopy` callbacks, then call `dvb_dmx_init` to expose the generic `struct dmx_demux` API.

## Important APIs, Types, And Functions

The exported entry points are `dvb_dmx_init`, `dvb_dmx_release`, `dvb_dmx_swfilter_packets`, `dvb_dmx_swfilter`, `dvb_dmx_swfilter_204`, and `dvb_dmx_swfilter_raw`. The init function allocates filter/feed arrays, initializes frontend and feed lists, installs default CRC and memcpy callbacks, and populates the `dmx_demux` vtable.

Software filtering is implemented by `dvb_dmx_swfilter_packet`, `_dvb_dmx_swfilter`, `find_next_packet`, and helpers for payload, PID, continuity, and speed checks. Section reconstruction uses `dvb_dmx_swfilter_section_packet`, `dvb_dmx_swfilter_section_copy_dump`, `dvb_dmx_swfilter_section_new`, `dvb_dmx_swfilter_section_feed`, and `dvb_dmx_swfilter_sectionfilter`.

Feed APIs are split between TS and section feeds. TS feed setup/start/stop/release flows through `dmx_ts_feed_set`, `dmx_ts_feed_start_filtering`, `dmx_ts_feed_stop_filtering`, `dvbdmx_allocate_ts_feed`, and `dvbdmx_release_ts_feed`. Section equivalents are `dmx_section_feed_set`, `dmx_section_feed_allocate_filter`, `prepare_secfilters`, `dmx_section_feed_start_filtering`, `dmx_section_feed_stop_filtering`, `dmx_section_feed_release_filter`, `dvbdmx_allocate_section_feed`, and `dvbdmx_release_section_feed`.

## Control Flow

TS input enters through either fixed-packet `dvb_dmx_swfilter_packets` or byte-stream `_dvb_dmx_swfilter`. The byte-stream path resynchronizes on 188-byte sync `0x47` or 204-byte Reed-Solomon packet marker `0xB8`, carries incomplete packets in `demux->tsbuf`, normalizes 204-byte packets to a 188-byte TS packet, and dispatches each packet under `demux->lock`.

`dvb_dmx_swfilter_packet` computes PID, optionally logs speed, handles TEI and continuity checking, sets buffer flags for matching feeds, and iterates `demux->feed_list`. Matching TS feeds either receive full packets, payload-only bytes, decoder writes, or DVR wildcard PID `0x2000` data. Matching section feeds reconstruct complete sections from payload units before invoking section callbacks.

Section reconstruction tracks `tsfeedp`, `secbufp`, `seclen`, CRC state, continuity counter, and whether PUSI was seen. PUSI splits payload into bytes before the next section and bytes after the new pointer boundary. Complete sections are length-checked, optionally CRC-checked, matched against all chained section filters using precomputed mask/mode arrays, delivered to `cb.sec`, then reset for the next section.

Feed allocation obtains an unused feed slot and sometimes an unused filter slot from vmalloc-backed arrays. Starting a feed calls the adapter's `start_feed`, then marks the feed filtering under the spinlock. Stopping calls `stop_feed`, clears filtering state, and moves the feed back to allocated/ready state. Release removes feeds from `feed_list`, frees filter state, clears PES reservations, and resets PID to `0xffff`.

## State And Persistence Behavior

`struct dvb_demux` owns all persistent in-memory state: users count, feed/filter arrays, frontend list, active frontend, active feed list, PES filter table and PID cache, TS resynchronization buffer, optional continuity counter storage, and counters for speed logging. There is no disk persistence.

`demux->mutex` protects high-level feed/frontend allocation and state transitions. `demux->lock` protects packet delivery, active feed list inspection, and filtering flags. Feed state moves through `DMX_STATE_FREE`, `DMX_STATE_ALLOCATED`, `DMX_STATE_READY`, and `DMX_STATE_GO`; callbacks are only supposed to receive data once filtering is active.

Section filter state is linked per feed via `dvb_demux_filter::next`. Filter masks are transformed at start time into `maskandmode`, `maskandnotmode`, and `doneq`, so runtime filtering can perform fast equality/inequality checks across `DVB_DEMUX_MASK_MAX`.

## Dependencies And Integration Points

The file depends on `media/dvb_demux.h`, the kernel CRC32 API, vmalloc allocation, user-copy helpers, spinlocks, mutexes, and `struct dmx_demux` contracts. It is used by demux device layers, DVR capture, DVB network decapsulation, and adapter hardware drivers that need a generic software filter in their interrupt/DMA receive path.

`dvbdmx_write` integrates memory frontends by copying user TS data into kernel memory and feeding it through `dvb_dmx_swfilter`. `add_frontend`, `connect_frontend`, and related methods integrate tuner/demux routing. `get_pes_pids` exposes cached PES PID assignments to callers.

## Risks And Edge Cases

The demux is sensitive to packet loss, TEI bits, continuity mismatches, PUSI boundaries, oversized sections, and bad pointer fields. It records buffer flags for downstream consumers, but callbacks need to interpret those flags correctly. If `dvb_demux_feed_err_pkts` is enabled, TEI-marked packets are still forwarded with flags; disabling it drops them.

Resource exhaustion returns `-EBUSY` when feed or filter arrays are full. PES decoder feeds reserve one `pes_type`, so duplicate decoder assignment returns `-EINVAL`. Release while filtering stops section feeds indirectly in `dmx_section_feed_release_filter`, but callers must respect the locking contract.

This snapshot has visible source-integrity concerns worth build-testing: `find_next_packet` contains a duplicated `break` indentation pattern, and `dmx_section_feed_start_filtering` appears to call `mutex_unlock(&dvbdmx->mutex)` twice on the no-filter error path. These are high-signal compile/static-analysis or review targets.

## Test Signals

Tests should feed clean and corrupted 188/204-byte packet streams, garbage before sync, split packets across calls, TEI packets with both `dvb_demux_feed_err_pkts` settings, continuity jumps, adaptation-only packets, payload-only TS feeds, wildcard DVR feeds, and section filters with positive and negative masks. Section tests should cover first-data-before-PUSI discard, pointer field boundaries, multiple sections in one TS payload, section padding, CRC pass/fail, and oversized section rejection.

Lifecycle tests should allocate all feeds/filters to confirm `-EBUSY`, start/stop TS and section feeds around adapter callback failures, release active section filters, connect/disconnect frontends, memory frontend `write`, and verify `dvb_dmx_release` frees all vmalloc-backed arrays.
