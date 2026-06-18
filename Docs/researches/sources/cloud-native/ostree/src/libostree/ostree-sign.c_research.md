# sources/cloud-native/ostree/src/libostree/ostree-sign.c

Purpose: implements the generic `OstreeSign` interface and shared workflows for commits, summaries, key loading, backend discovery, and stream readers. It bridges backend-specific engines with repository detached metadata and summary signature persistence.

Important APIs/types/functions: `sign_types` maps names to GTypes depending on compile flags, always including dummy. Generic wrappers cover metadata key/format, key clearing/setting/loading, data sign/verify, and engine name. `_sign_detached_metadata_append` appends a signature byte array to a metadata dictionary under the backend key. `ostree_sign_commit_verify` loads commit data and detached metadata then delegates to `data_verify`. `ostree_sign_commit` signs commit bytes and writes updated detached metadata. `ostree_sign_get_all` and `ostree_sign_get_by_name` instantiate backends. `_ostree_sign_summary_at` signs `summary` for each key and writes normalized `summary.sig`. `ostree_sign_read_pk/sk` select base64, PEM, or raw blob readers by backend type.

Control flow: generic methods assert the interface, check backend vfunc availability, and return "not implemented" otherwise. Commit signing loads the commit variant, reads existing detached metadata, signs serialized commit bytes, appends the signature, and writes metadata. Commit verification extracts the backend signature array and asks the backend to verify. Summary signing opens `summary`, optionally reads `summary.sig`, rejects empty key arrays, sets the backend secret key for each key, signs, appends metadata, and replaces `summary.sig`. Backend lookup lazily initializes GTypes.

State/persistence: backend instances hold keys. Persistent outputs are commit detached metadata and `summary.sig`, both as normalized `GVariant` dictionaries keyed by backend metadata names. `ostree_sign_get_all` returns fresh engine instances.

Dependencies/integration: depends on GLib/GObject/GVariant/GBytes, libglnx, fd/mmap utilities, OSTree core/repo-private APIs, blob readers, backend headers, and repository detached metadata/summary helpers. Integrated by CLI signing, summary regeneration, static delta signatures, pull/verify code, and tests.

Risks: signature append relies on backend metadata format strings matching detached metadata contents. `ostree_sign_commit_verify` passes `NULL` signatures when metadata is absent, so backend diagnostics matter. Summary signing sets secret keys sequentially; some backends clear all keys on `set_sk`. `ostree_sign_get_all` asserts construction success. Dummy is always registered but guarded at operation time.

Test signals: dummy, Ed25519, SPKI, commit-sign, delta-sign, summary-signature, signed-pull, and composefs signed tests exercise commit metadata append/verify, summary signatures, backend selection, key readers, and failure diagnostics.
