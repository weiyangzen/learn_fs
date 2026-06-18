# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx.h

Purpose: Declares HIF command serialization state and high-level WFx request helper APIs.

Important APIs and types: `struct wfx_hif_cmd` contains a mutex, ready/done completions, outgoing buffer pointer, incoming reply pointer/length, and return code. Exports `wfx_init_hif_cmd()`, `wfx_cmd_send()`, MIB read/write, start/reset/join/map-link/key/PM/BSS/EDCA/beacon/scan/configuration/shutdown helpers.

Control flow and integration: Common probe initializes this state in `wfx_init_common()`. BH consumes `hif_cmd.ready` before data queues, and HIF RX completes `done` on matching confirmations.

State and persistence: The struct is transient per synchronous command and persists as a per-device serialization object.

Dependencies: Depends on Linux mutex/completion, HIF message type, and mac80211/cfg80211 forward declarations.

Risks and test signals: Tests should verify commands cannot overlap, no-reply commands flush the BH workqueue, and callers respect reply buffer sizes for MIB reads.

Test signals: Source read size: 62 lines, 2527 bytes.
