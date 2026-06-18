# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_crypto.h

Purpose: declares common GSS crypto helper types and functions used by Kerberos and shared-key mechanisms.

Important APIs/types/functions: `struct gss_keyblock` pairs a `rawobj_t` key with a synchronous skcipher transform. Prototypes cover keyblock lifecycle, serialized context parsing, sgtable setup/teardown, generic encryption, digest hashing, compatibility hashing, padding, and raw object encryption/decryption.

Control flow: no executable flow. Mechanisms include this header and call helper functions during context import, MIC generation, wrap/unwrap, and bulk encryption.

State/persistence: the header defines ownership expectations for keyblocks but stores no state itself.

Dependencies/integration: includes Linux scatterlist and skcipher headers plus `gss_internal.h`, so users inherit raw object definitions and Lustre security declarations.

Risks/test signals: this is an internal contract; signature changes must be reflected in every mechanism. Compile tests with Kerberos and SSK enabled are the main signal, plus unit coverage of helper behavior in `gss_crypto.c`.
