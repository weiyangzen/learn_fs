# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-object-version.h

Purpose: this header declares the compact on-disk xattr payload formats for bit-rot object versioning and signing.

Important types: `br_version_t` stores `ongoingversion` plus a two-word timestamp buffer. `br_signature_t` is packed and stores `signaturetype`, `signedversion`, and a flexible `signature[]` payload. These are the concrete values persisted under `BITROT_CURRENT_VERSION_KEY` and `BITROT_SIGNING_VERSION_KEY`.

Control flow role: bit-rot-stub initializes these records on lookup/create/mknod, updates `br_version_t` before modifying writes or truncates, and writes `br_signature_t` when bitd submits a validated signature. The scrubber and bitd later read them through virtual signature queries to determine staleness and verify content.

State and persistence behavior: this file is entirely about persistence layout. Any ABI change affects existing brick xattrs. The packed attribute on `br_signature_t` avoids compiler padding before the flexible signature payload.

Dependencies and integration points: included by `bit-rot-common.h`, which supplies helper functions for populating these records. It assumes standard integer and endian types are already available through surrounding GlusterFS headers.

Risks: the use of `unsigned long` in on-disk structures may be sensitive to architecture width and endian interpretation. Tests should guard mixed-version and mixed-architecture compatibility if the format is ever changed.

Test signals: validate xattr byte sizes for default signatures and SHA256 signatures, verify no padding is introduced in `br_signature_t`, and exercise upgrade/missing-xattr paths.
