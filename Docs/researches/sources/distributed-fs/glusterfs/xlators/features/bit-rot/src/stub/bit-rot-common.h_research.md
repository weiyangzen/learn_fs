# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-common.h

Purpose: this shared header defines bit-rot xattr state classification, in-memory signature payloads, stub initialization payloads, signature type constants, and helpers for converting daemon requests into on-disk version/signature records. It is included by both bit-rot daemon and stub code.

Important APIs and types: `br_vxattr_status_t` classifies xattr combinations as full, missing, unsigned, or invalid. `br_sign_state_t` describes release/signing state transitions: normal, reopen-wait, and quick sign. `br_version_xattr_state` examines a dict for `BITROT_OBJECT_BAD_KEY`, `BITROT_CURRENT_VERSION_KEY`, and `BITROT_SIGNING_VERSION_KEY`. `br_isignature_t` is the daemon-to-stub signing request format, and `br_isignature_out_t` is the stub-to-daemon/scrubber signature query format. `br_stub_init_t` carries stub boot time and brick export. Helpers set default versions, default signatures, ongoing versions, and packed signatures.

Control flow role: stub lookup/getxattr code uses `br_version_xattr_state` to decide whether an object is signed, unsigned, missing all bitrot metadata, or corruptly inconsistent. Daemon code constructs `br_isignature_t`, passes it under `GLUSTERFS_SET_OBJECT_SIGNATURE`, and the stub uses `br_set_signature` to persist it as `BITROT_SIGNING_VERSION_KEY`.

State and persistence behavior: the header defines names for the virtual stub init xattr and reopen hint xattr. It also defines the bad-object container GFID constant and the transient/persistent signature types. The on-disk persistence layout itself is declared in `bit-rot-object-version.h`, but this file provides the functions that populate it.

Dependencies and integration points: it depends on GlusterFS dict and bitrot key definitions supplied elsewhere, plus network byte order helpers used by the stub. It is a protocol boundary between daemon, scrubber, and stub, so additions must remain binary-compatible with existing xattr values.

Risks: `br_version_xattr_state` treats the mere presence of the bad-object key as enough to mark an object bad. Incorrect dict population can therefore cause EIO behavior for otherwise readable files. Signature length handling relies on caller-provided sizes and flexible arrays, so bounds and endian conversions are important.

Test signals: test all four xattr state combinations, bad-object detection with and without version/signature keys, signature type validation, default version/signature initialization, and daemon-stub round trips for SHA256 signatures.
