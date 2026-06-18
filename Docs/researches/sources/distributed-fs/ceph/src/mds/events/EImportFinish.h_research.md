# sources/distributed-fs/ceph/src/mds/events/EImportFinish.h

Purpose: Declares the event marking completion of a subtree import attempt.

Important APIs/types: `EImportFinish` stores base imported dirfrag and a success flag, with encode/decode/dump/test generation and replay.

Control flow: Import code writes this after an import succeeds or fails; replay can finalize or unwind import state based on `success`.

State and persistence behavior: Persistent payload is minimal: base dirfrag plus boolean outcome. It does not expose a metablob.

Dependencies and integration points: Uses `MDSRank`, `LogEvent`, and migration/import state machines.

Risks: Missing or wrong success state can leave an imported subtree ambiguous or incorrectly authoritative after replay.

Test signals: Replay success and failure imports, especially after importer/exporter failover.
