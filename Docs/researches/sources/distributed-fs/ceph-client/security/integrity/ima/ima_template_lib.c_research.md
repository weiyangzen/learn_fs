# sources/distributed-fs/ceph-client/security/integrity/ima/ima_template_lib.c

Purpose: Implements serialization, display, parsing, and field initialization helpers for all supported IMA measurement template fields.

Important APIs/types/functions: Provides show functions for digest/string/signature/buffer/uint fields, `ima_parse_buf()`, digest initializers (`ima_eventdigest_init`, `_ng_init`, `_ngv2_init`, `_modsig_init`), event name initializers, signature/buffer/modsig/EVM signature field initializers, inode DAC fields, and protected xattr field initializers.

Control flow: Field initializers populate `struct ima_field_data` with allocated buffers using `ima_write_template_field_data()`, which NUL-terminates string data and replaces spaces with underscores for ASCII measurement parsing. Digest initialization chooses legacy, algorithm-prefixed, or type+algorithm-prefixed formats; violation events reserve zero/empty digest-sized fields. Display helpers render either ASCII or binary, respecting canonical endian format for integer field lengths and values. `ima_parse_buf()` walks serialized length-prefixed fields with optional fixed-length masks and strict end/field enforcement.

State and persistence: It allocates per-entry template field data but owns no global state. It depends on `ima_canonical_fmt`, `ima_hash_algo`, event data, and file xattrs at initialization time.

Dependencies and integration: Integrates with fs-verity digest type signaling, modsig helpers, EVM protected xattr readers, file hash calculation, boot aggregate calculation, seq_file output, and kexec restore parsing.

Risks and test signals: Important risks are bounds arithmetic in `ima_parse_buf()`, digest format compatibility, silent zero-length fields for missing optional data, xattr allocation failures returning success with empty fields, and canonical endian handling. Tests should cover ASCII/binary rendering, filenames with spaces, violation records, modsig digest/raw signature fields, EVM portable signatures, protected xattr lists, and malformed serialized buffers.
