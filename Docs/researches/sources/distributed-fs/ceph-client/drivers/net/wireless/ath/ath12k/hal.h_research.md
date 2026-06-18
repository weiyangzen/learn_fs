# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hal.h

## Purpose

`hal.h` defines ath12k hardware abstraction constants, descriptor/ring enums, RX monitor status structures, SRNG state, REO command structures, hardware register maps, HAL ops, and public HAL helper prototypes. It is the central contract between generic datapath code and hardware-specific ath12k implementations.

## Important APIs, Types, and Functions

The header defines ring IDs in `enum hal_srng_ring_id`, ring types in `enum hal_ring_type`, ring direction and MAC type enums, SRNG flags, interrupt mitigation thresholds, and `struct hal_srng_config`, `hal_srng_params`, and `hal_srng`.

RX/monitor metadata types include `hal_rx_user_status`, `hal_rx_u_sig_info`, `hal_rx_tlv_aggr_info`, `hal_rx_eht_info`, `hal_rx_msdu_desc_info`, `hal_mon_buf_ring`, `hal_rx_mon_ppdu_info`, and `hal_rx_desc_data`. These carry PPDU IDs, rates, MCS/NSS/BW/GI, EHT/HE radiotap data, user stats, RSSI, addresses, crypto/decap state, and descriptor-derived RX status fields.

Buffer and descriptor types include `ath12k_buffer_addr`, `hal_wbm_link_desc`, `hal_wbm_idle_scatter_list`, `ath12k_hal_reo_cmd`, `hal_reo_status_header`, and CE descriptor forward declarations.

Hardware-level state is represented by `ath12k_hw_hal_params`, `ath12k_hw_regs`, `ath12k_hal`, `ath12k_hal_tcl_to_wbm_rbm_map`, and `ath12k_hw_version_map`.

`struct hal_ops` declares hardware-specific callbacks for SRNG config/ring ID/setup, RX descriptor parsing, CE descriptors, TX bank/DSCP configuration, REO queue LUT and hardware setup, buffer address encoding, current channel config, idle link RBM, MSDU list extraction, and TLV encode/decode variants.

Public prototypes expose the SRNG, CE, REO, RX buffer, shadow config, stats dump, and TLV helpers implemented by `hal.c`.

## Control Flow and Integration

Hardware-specific files populate `ath12k_hw_version_map` with `hal_ops`, descriptor sizes, register maps, RBM maps, and HAL params. Core initialization copies those into `ab->hal`, then `hal.c` creates SRNG config and initializes common ring state. Datapath code uses the public helpers and inline structures to post RX/TX buffers, parse completions, configure REO queues, and decode monitor TLVs without embedding chip-specific descriptor layouts.

## State and Persistence Behavior

Most structures here describe long-lived hardware/shared-memory state: ring pointers, coherent pointer memory, register offsets, buffer cookies, REO queue settings, and monitor PPDU status. Many fields are shared with firmware/hardware through DMA or MMIO, so layout, alignment, endianness, and bit masks are persistent interface contracts.

## Dependencies and Integration Points

`hal.h` includes `hw.h`, creating a close coupling between hardware parameter definitions and HAL definitions. It also references mac80211 radiotap/rate types, Linux DMA addresses, lockdep keys, HAL RX descriptor forward declarations, and ath12k core structures.

## Risks and Contract Notes

- The header includes `hw.h` while `hw.h` includes `hal.h`; include guards prevent recursion, but this circular relationship makes forward declaration hygiene important.
- Ring ID ranges and derived constants such as `HAL_SRNG_RING_ID_MAX` must match hardware-specific ops and register maps exactly.
- `struct hal_rx_mon_ppdu_info` is large and accumulates many optional TLV-derived fields; parsers must carefully reset it between PPDUs.
- `ath12k_he_ru_tones_to_nl80211_he_ru_alloc()` maps unsupported/default cases to 26-tone RU, which can hide unexpected RU values.
- Public structures use packed hardware layouts and little-endian fields; accidental host-endian access would corrupt descriptors.
- Many ops are mandatory in practice despite being function pointers; hardware map initialization must provide a complete ops table.

## Test Signals

Build all hardware variants, run sparse/endian checks on descriptor fields, validate ring ID/config tables against hardware docs, exercise RX/TX/CE/monitor/REO paths, run radiotap HE/EHT capture validation, and use lockdep/KASAN with SRNG wraparound traffic.
