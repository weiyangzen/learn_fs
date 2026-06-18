# sources/distributed-fs/ceph-client/security/integrity/ima/ima_template_lib.h

Purpose: Declares the IMA template field library interface shared by template descriptor management and measurement rendering/restoration code.

Important APIs/types/functions: Defines `ENFORCE_FIELDS` and `ENFORCE_BUFEND` parse flags and prototypes for field show functions, `ima_parse_buf()`, and all event field initializers for digests, names, signatures, buffers, inode uid/gid/mode, and protected xattr names/lengths/values.

Control flow: The header has no runtime flow but establishes the function table contract used by `supported_fields[]` in `ima_template.c`; each field descriptor maps a field id to an initializer and a display function declared here.

State and persistence: No persistent state. The declared functions allocate or display per-measurement field data owned by template entries.

Dependencies and integration: Includes `ima.h` and `linux/seq_file.h`, exposing APIs to IMA template core while hiding implementation details in `ima_template_lib.c`.

Risks and test signals: Interface risks are prototype drift against `supported_fields[]` and parse flag misuse by restore code. Build tests catch signature mismatch; runtime tests should validate field ids and parsing behavior through template initialization and kexec restore.
