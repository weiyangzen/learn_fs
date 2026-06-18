# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp.h

## Purpose

`ice_ptp.h` is the public ICE PTP subsystem header. It documents the hardware timestamp block model, defines core software tracking structures for Tx timestamp requests and PTP ports, describes PHC/pin state stored in `struct ice_ptp`, declares register address helper macros used by the implementation, and exposes PTP APIs to the rest of the driver when `CONFIG_PTP_1588_CLOCK` is enabled.

The header also provides no-op or `-EOPNOTSUPP` inline stubs when PTP support is compiled out, allowing the rest of the ICE driver to call timestamp hooks without spreading conditional compilation through datapath and reset code.

## Important APIs, Types, And Functions

- `struct ice_tx_tstamp` stores one outstanding Tx timestamp request: SKB pointer, start jiffies, and cached timestamp value.
- `enum ice_tx_tstamp_work` defines completion versus pending work status, though this file's current implementation paths primarily process timestamps through IRQ/threaded work.
- `struct ice_ptp_tx` tracks all Tx timestamp slots for a port, including spinlock, request array, `in_use` and `stale` bitmaps, hardware block/offset/length mapping, initialization/calibration flags, ready-bitmap support, and low-latency read index.
- `INDEX_PER_QUAD`, `INDEX_PER_PORT_E82X`, and `INDEX_PER_PORT` describe timestamp register partitioning for shared E82X quad blocks and per-port blocks.
- `struct ice_ptp_port` combines a Tx tracker, calibration delayed work, PHY-start mutex, link state, FIFO retry state, and logical port number.
- `enum ice_ptp_tx_interrupt` models disabled, self-handled, and owner-handled Tx timestamp interrupt processing.
- `enum ice_ptp_state` models uninitialized, initializing, ready, resetting, and error states.
- `enum ice_ptp_pin` and `enum ice_ptp_pin_nvm` identify logical PTP-capable pins and NVM pin names.
- `GLTSYN_AUX_OUT`, `GLTSYN_AUX_IN`, `GLTSYN_CLKO`, `GLTSYN_TGT_*`, and `GLTSYN_EVNT_*` macros calculate per-channel register addresses.
- `struct ice_ptp_pin_desc` maps a PTP pin name to input/output GPIO numbers and per-direction delay compensation.
- `struct ice_ptp` stores the full PF PTP state, PTP clock registration data, cached PHC time, pin state, cached perout/extts requests, hwtstamp config, reset-time snapshot, counters, and worker state.
- Exported prototypes cover hwtstamp get/set, timestamp mode restore, external timestamp events, Tx timestamp slot request and completion, IRQ processing, pending timestamp checks, PHC reads, Rx timestamp conversion, reset/rebuild, init/release, link change, work queueing, and clock index lookup.

## Control Flow

This header does not implement runtime control flow, but it defines the contracts followed by `ice_ptp.c` and driver call sites. Datapath code requests Tx slots through `ice_ptp_request_ts()` and receives `-1` when no slot is available or PTP is unavailable. Rx code calls `ice_ptp_get_rx_hwts()` and receives zero when no valid timestamp can be reported. Reset and link code call `ice_ptp_prepare_for_reset()`, `ice_ptp_rebuild()`, and `ice_ptp_link_change()` to keep PHC and PHY timestamp state synchronized with device state.

The conditional compilation block is a control-flow boundary for the broader driver. With `CONFIG_PTP_1588_CLOCK`, the prototypes resolve to real functions in `ice_ptp.c`. Without it, calls compile to inert inline functions: hwtstamp operations fail with `-EOPNOTSUPP`, timestamp requests fail, timestamp processing does nothing, pending checks are false, PHC reads and Rx timestamps return zero, and lifecycle hooks are no-ops.

## State And Persistence

The header defines in-memory state shapes but does not persist data itself. `struct ice_ptp` is embedded in `struct ice_pf` and persists for the life of that PF instance. It caches user-requested timestamp configuration, perout/extts requests, the registered PTP clock pointer, delayed work and worker handles, and counters. `struct ice_ptp_tx` owns dynamically allocated arrays/bitmaps while initialized, and each timestamp slot temporarily owns a referenced SKB until completion, timeout, stale discard, or flush.

Hardware and firmware state are represented indirectly through register constants and block/offset fields. The comments document that hardware timestamp registers are read-only from the software perspective and are not automatically cleared except by reset or new captures, which explains why software must prevent timestamp slot reuse and may need cached-value stale detection on hardware without ready bitmaps.

## Dependencies And Integration Points

The header depends on Linux PTP clock definitions, kthread delayed work support, and `ice_ptp_hw.h` for hardware PTP constants and types. It relies on surrounding ICE driver declarations such as `struct ice_pf`, `struct ice_hw`, `struct net_device`, `struct sk_buff`, RX descriptor types, packet context, reset enums, and IRQ return types.

It is included by ICE implementation files that need PTP support: the PTP implementation, transmit datapath, receive timestamp extraction helpers, netdevice operations, reset/link handling, and code that reports the PHC index. Its stub block is an important integration point because it keeps those call sites buildable when the kernel PTP clock framework is disabled.

## Risks

- The Tx timestamp model depends on software-exclusive slot allocation. Misusing `struct ice_ptp_tx` without holding its spinlock or without respecting `init`/`calibrating` can corrupt SKB ownership or reuse a hardware index too early.
- The `last_ll_ts_idx_read` field is signed while most indexes are unsigned; code must preserve the `-1` sentinel and avoid accidental wrap assumptions.
- The hardware block diagrams and index constants encode family-specific timestamp register partitioning. Any future hardware with different sharing or per-port sizes needs careful updates to both comments and initialization logic.
- The fallback stubs intentionally hide PTP absence behind successful no-ops in many lifecycle paths. Callers that need to distinguish "compiled out" from "temporarily unavailable" must use the hwtstamp return values or clock index.
- `struct ice_ptp` combines state used from IRQ, kthread, reset, datapath, and userspace callback contexts. New fields need explicit locking or lifetime rules consistent with the implementation.

## Test Signals

Build coverage should include both `CONFIG_PTP_1588_CLOCK=y/m` and disabled configurations to verify real prototypes and stubs remain compatible with call sites. Runtime tests should confirm Tx timestamp request failure paths when trackers are uninitialized or full, cleanup of SKB references on release/reset, PHC clock index reporting, hwtstamp unsupported behavior in non-PTP builds, and correct per-family tracker sizing for E810/E830/E82X/E825C. Static analysis should focus on bitmap bounds, signed/unsigned index handling, and cross-context access to `struct ice_ptp` fields.
