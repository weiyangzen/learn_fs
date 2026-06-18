# sources/distributed-fs/ceph-client/net/nfc/hci/llc.c

Purpose: Manages pluggable HCI Link Layer Control engines and provides a uniform allocation/start/stop/rx/tx wrapper around NOP and SHDLC LLC implementations.

Important APIs and functions: `nfc_llc_init`, `nfc_llc_exit`, `nfc_llc_register`, `nfc_llc_allocate`, `nfc_llc_free`, `nfc_llc_start`, `nfc_llc_stop`, `nfc_llc_rcv_from_drv`, `nfc_llc_xmit_from_hci`, and `nfc_llc_get_data` are the main entry points. `nfc_llc_register` stores `struct nfc_llc_engine` records in a global list.

Control flow: Subsystem init registers the NOP engine and, conditionally, SHDLC. Allocation looks up an engine by name, allocates `struct nfc_llc`, calls the engine's `init`, stores rx headroom/tailroom, and returns a wrapper used by HCI core. Runtime calls are direct ops-table dispatches.

State and persistence: The global `llc_engines` list persists registered engines until `nfc_llc_exit`. Each allocated `struct nfc_llc` persists engine private state in `data` plus selected ops and rx head/tailroom.

Dependencies and integration points: Included by the HCI core allocation path. Engine names come from public `<net/nfc/llc.h>` constants and local `llc.h` ops.

Risks: The engine list is not protected by a lock; this is acceptable for init/exit-only registration but would be unsafe for dynamic runtime registration. Duplicate engine names are not rejected. Allocation returns NULL for unknown names without error detail.

Test signals: Validate init rollback if either engine registration fails, name lookup, allocation/deallocation paths, ops dispatch, duplicate-name behavior if registration becomes dynamic, and rx headroom propagation.
