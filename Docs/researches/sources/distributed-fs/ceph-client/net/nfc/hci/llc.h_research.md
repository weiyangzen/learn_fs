# sources/distributed-fs/ceph-client/net/nfc/hci/llc.h

Purpose: Defines the internal LLC engine interface used by the HCI core to abstract different link-layer framing protocols.

Important APIs and types: `struct nfc_llc_ops` defines `init`, `deinit`, `start`, `stop`, `rcv_from_drv`, and `xmit_from_hci`. `struct nfc_llc_engine` records a registered engine name and ops. `struct nfc_llc` holds engine private data, ops, and receive headroom/tailroom. The header declares NOP and SHDLC registration functions.

Control flow: Engines implement the ops contract, `llc.c` registers engines and dispatches through this table, and the HCI core uses only the wrapper functions exported from `llc.c`.

State and persistence: No state is directly stored by the header, but its structures define the lifetime and ownership of engine private data.

Dependencies and integration points: Includes public NFC HCI and LLC headers and Linux skb types. The SHDLC registration declaration is compiled out to a no-op when `CONFIG_NFC_SHDLC` is disabled.

Risks: Engine callbacks receive raw skb ownership; each engine must consistently free or transfer skbs. The `init` callback returns a void pointer, so type safety for private data is entirely by convention.

Test signals: Build with and without `CONFIG_NFC_SHDLC`, verify ops signatures remain synchronized with all engines, and run ownership tests for tx/rx skb behavior.
