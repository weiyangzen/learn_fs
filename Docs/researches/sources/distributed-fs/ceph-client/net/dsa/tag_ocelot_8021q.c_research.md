# sources/distributed-fs/ceph-client/net/dsa/tag_ocelot_8021q.c

Purpose: Ocelot/Felix DSA tagger that uses the generic tag_8021q format and switch TCAM rules instead of NPI headers, preserving functionality under VLAN-filtering bridges.

Important APIs/types: `struct ocelot_8021q_tagger_private` embeds exported `ocelot_8021q_tagger_data` and a kthread worker. `ocelot_defer_xmit()` queues switch-driver deferred transmit work for PTP/link-local frames. `ocelot_xmit()` uses tag_8021q for normal data. `ocelot_rcv()` decodes tag_8021q and maps the user port. Connect/disconnect manage the worker.

Control flow: normal TX inserts an 802.1Q tag with PCP and standalone VID. PTP rewrite or link-local traffic is deferred to switch-driver work and has checksums completed in software if needed. RX calls `dsa_8021q_rcv()`, maps source switch/port, and marks hardware-forwarded frames.

State and persistence: per-switch runtime state in `ds->tagger_data`; no persistence. Worker lifetime follows tagger connect/disconnect.

Dependencies and integration: depends on generic tag_8021q helpers, Ocelot PTP helpers, DSA tagger-data contracts, kthread workers, and Felix driver callback setup.

Risks and test signals: deferred transmit reference ownership and checksum completion are the sensitive paths. Tests should cover normal data, PTP over IP, link-local control, worker setup failure, source decoding, and bridge/VLAN-aware operation.
