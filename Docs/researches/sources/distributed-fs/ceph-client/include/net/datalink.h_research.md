# sources/distributed-fs/ceph-client/include/net/datalink.h

Read `sources/distributed-fs/ceph-client/include/net/datalink.h` completely for this pass (26 lines, 590 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/datalink.h_research.md`.

Purpose: defines the small protocol descriptor used by legacy INET datalink/LLC integration to bind a link-layer protocol type, SAP, header length, receive callback, and header request callback.

Important APIs/types/functions: `struct datalink_proto` contains an 8-byte type field, `struct llc_sap *sap`, `header_length`, `rcvfunc()` for receive delivery, `request()` for building/requesting a datalink header into an skb, and a list node.

Control flow: datalink protocol registration code links descriptors onto a list. Receive paths call `rcvfunc()` with skb, input device, packet type, and original device. Transmit/header-building paths call `request()` with the datalink protocol, skb, and destination address bytes.

State and persistence: descriptors are list-managed runtime registrations. The header defines no allocator or lifecycle; owner modules must keep callback and SAP storage valid while registered.

Dependencies and integration points: depends on LLC SAPs, netdevices, packet types, skbuffs, and legacy IP-over-LLC/datalink code.

Risks: callbacks are raw function pointers with lifetime requirements. The fixed 8-byte `type` field and separate `header_length` must match the protocol's actual header layout. List membership must be synchronized by the owner.

Test signals: protocol registration/removal tests, receive callback dispatch, header construction for LLC/SNAP-like payloads, module unload while registered, and malformed destination/header length cases.
