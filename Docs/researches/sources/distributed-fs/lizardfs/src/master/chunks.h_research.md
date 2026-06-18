# sources/distributed-fs/lizardfs/src/master/chunks.h

Purpose: public interface for the master chunk metadata subsystem.

Important APIs/functions: version and file-reference updates (`chunk_increase_version`, `chunk_set_version`, `chunk_change_file`, `chunk_delete_file`, `chunk_add_file`), locking (`chunk_unlock`, `chunk_can_unlock`), modifications (`chunk_apply_modification`, live `chunk_multi_modify`, `chunk_multi_truncate`), stats (`chunk_stats`, `chunk_store_info`, `chunk_get_missing_count`, `chunk_store_chunkcounters`, `chunk_count`, replication/availability accessors, `chunk_info`), repair/location/copy callbacks, load/store lifecycle, checksum, and background checksum update.

Control flow: master modules call these functions from filesystem operations, chunkserver protocol handlers, metadata load/store, and daemon initialization. `METARESTORE` builds expose dump but omit live chunkserver APIs.

State and persistence: declared functions manipulate state owned by `chunks.cc`; load/store functions persist chunk metadata.

Dependencies and integration: includes chunk part/address types, chunk availability state, client-master protocol types, and checksum modes; forward-declares `matocsserventry`.

Risks: broad C-style interface exposes many state transitions without type-level sequencing guarantees; callers must respect lock/version semantics and live-vs-restore compile modes.

Test signals: linked into master unit/integration tests; no direct header-only tests.
