# sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_powerpc.c

Purpose: Loads powerpc secure variable certificate and revocation databases into keyrings/blacklists.

Important APIs/types/functions: `get_cert_list()` reads a named secure variable into kmalloc memory. `load_powerpc_certs()` handles db, dbx, trustedcadb, and moduledb and is registered with `late_initcall`.

Control flow: It requires `secvar_ops`, checks the firmware format string against supported OPAL/PLPKS secure boot formats, applies an 8-byte timestamp offset for PLPKS variables, reads each database, logs absent optional variables, parses EFI signature lists with the correct handler selector, frees buffers, and returns the last non-fatal parse/read status.

State and persistence: Local buffers are transient; parsed certificates and hashes persist in platform, machine, secondary, or blacklist keyrings.

Dependencies and integration: Depends on powerpc secure variable ops, secure boot formats, EFI signature parser, keyring handler selectors, and integrity keyring APIs.

Risks and test signals: Risks include offset/size underflow in `extract_esl`, unsupported format rejection, inconsistent error propagation across multiple variables, and malformed ESL parsing. Tests should use fake secvar ops for absent, error, unsupported, PLPKS-offset, and malformed database cases.
