# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi.h

Purpose: Declares the public GSI subsystem data structures and API used by the IPA driver. It defines ring, transaction-pool, channel, event-ring, and top-level GSI state structures plus lifecycle/channel-control entry points.

Important APIs/types: `GSI_CHANNEL_COUNT_MAX`, `GSI_EVT_RING_COUNT_MAX`, and `GSI_TLV_MAX` bound driver-supported hardware. `struct gsi_ring` tracks DMA-coherent ring virtual/DMA addresses, count, and software index. `struct gsi_trans_pool` and `struct gsi_trans_info` describe fixed pools and transaction state cursors. `enum gsi_channel_state` and `enum gsi_evt_ring_state` mirror hardware states. `struct gsi_channel` combines topology, ring pointers, TX accounting, transaction info, and NAPI. `struct gsi` stores device, version, register mapping, IRQ masks, completions, mutex, channel/event arrays, and dummy netdev.

Control flow and integration: Public functions declared here are implemented by `gsi.c` and called by IPA core and endpoint code. `gsi_init()` runs before hardware readiness; `gsi_setup()` runs after firmware/early GSI enablement; `gsi_teardown()`/`gsi_exit()` undo those phases. Channel start/stop/reset/suspend/resume are called by endpoint and power paths. `gsi_channel_tre_max()` informs transaction and command-pool sizing.

State and persistence: This header defines the in-memory state model. Ring indices are volatile software cursors; transaction cursors model free/allocated/committed/pending/completed/polled lifetimes; IRQ bitmaps cache programmed masks. No persistent storage is declared.

Dependencies: Includes Linux completion, mutex, netdevice, and type headers plus `ipa_version.h`. It forward-declares platform, endpoint, and transaction types to avoid broad include coupling.

Risks: Consumers must respect phase ordering: `gsi_init()` before setup, setup before channel start, stop before reset/teardown, and exit after teardown. Cursor fields in `gsi_trans_info` are tightly coupled to modulo ring sizes; changing ring sizing rules requires reviewing transaction code. `GSI_CHANNEL_COUNT_MAX`/event max are driver caps, not necessarily hardware caps.

Test signals: Compile-time checks validate type visibility. Runtime test signals are successful init/setup/exit pairing, channel lifecycle tests, and transaction allocation pressure tests that do not corrupt cursor state.
