# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_lockingver.h

Purpose: declares the OCFS2 cluster locking protocol version used by locking negotiation.

Important APIs and types: `OCFS2_LOCKING_PROTOCOL_MAJOR` and `OCFS2_LOCKING_PROTOCOL_MINOR` are currently `1` and `0`, documented as the initial protocol from OCFS2 1.4.

Control flow: this header has no code; DLM glue and mount/cluster negotiation code include the version constants to advertise or verify locking compatibility.

State and persistence: no storage is defined here. The constants are runtime protocol ABI rather than filesystem metadata.

Dependencies and integration: integrates with `dlmglue.c` and cluster stack compatibility checks. It is intentionally small so every participant compiles against the same version constants.

Risks: bumping the version without matching negotiation behavior can split clusters or allow incompatible nodes to coordinate incorrectly. Failing to bump it when lock semantics change can cause subtle cross-version corruption.

Test signals: mixed-version cluster mount tests, lock negotiation failure tests, DLM protocol logging, and rolling-upgrade scenarios that verify expected accept/reject behavior.
