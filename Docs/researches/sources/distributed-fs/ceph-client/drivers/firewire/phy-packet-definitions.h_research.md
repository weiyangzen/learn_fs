<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/phy-packet-definitions.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/phy-packet-definitions.h

Purpose: defines packet-field helpers for IEEE 1394 PHY packets, especially PHY config packets and self-ID packets. It is used by the OHCI driver to decode self-ID streams and to synthesize a missing local self-ID for a TI erratum, and by KUnit tests to validate serialization.

Important APIs and control flow: common helpers get/set the two-bit packet identifier. PHY config helpers get/set root ID, force-root-node, gap-count optimization, and gap count. Self-ID helpers get/set PHY ID, extended flag, more-packets flag, link-active, gap count, speed code, contender, power class, initiated-reset, and extended-packet sequence. `struct self_id_sequence_enumerator` plus `self_id_sequence_enumerator_next()` walks a buffer of self-ID quadlets one node sequence at a time, validating maximum quadlet count, extended packet markers, and sequence numbers. Port helpers compute capacity as `quadlet_count * 8 - 5` and get/set two-bit port statuses across base and extended self-ID quadlets.

State and persistence behavior: no global state exists. The enumerator mutates only its cursor and remaining quadlet count, allowing callers to incrementally consume a self-ID stream.

Dependencies and integration points: consumed by `ohci.c` for self-ID decoding, ordering by PHY ID, port-status synthesis in `find_and_insert_self_id()`, and bus-reset handoff to the FireWire core. Consumed by `packet-serdes-test.c` for round-trip coverage. It depends on Linux error-pointer conventions and errno values for enumerator failures.

Risks and test signals: `phy_packet_self_id_extended_set_sequence()` shifts by `SELF_ID_EXTENDED_SHIFT` instead of `SELF_ID_EXTENDED_SEQUENCE_SHIFT`, which is masked afterward and is suspicious even if current test vectors may not expose every sequence value. Helpers do not range-check inputs. `self_id_sequence_get_port_capacity()` underflows if called with zero quadlets. Enumerators return `ERR_PTR(-ENODATA)` and `ERR_PTR(-EPROTO)`, so callers must use error-pointer checks. Test signals include KUnit self-ID and PHY config round trips, OHCI bus reset handling with multi-quadlet self-ID sequences, correct port topology reported to the FireWire core, and explicit tests for enumerator malformed-sequence paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/phy-packet-definitions.h -->
