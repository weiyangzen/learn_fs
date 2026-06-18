<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/error.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/error.h

Purpose: public error-reporting header for CAAM modules.

Important APIs and control flow: declares `caam_strstatus()`, convenience macros `caam_jr_strstatus()` and `caam_qi2_strstatus()`, `caam_dump_sg()`, and inline `is_mdha()` for checking whether an algorithm selector targets MDHA hash hardware. It also defines `CAAM_ERROR_STR_MAX`.

State and persistence behavior: none in the header; it references error-reporting functions and constants implemented in `error.c`.

Dependencies and integration points: includes `desc.h` for operation selector constants and is used by callbacks and descriptor builders that need consistent status-to-errno conversion or MDHA detection.

Risks and test signals: risks include `CAAM_ERROR_STR_MAX` not being tied to actual emitted strings and `caam_qi2_strstatus()` passing a flag not currently distinguished by `caam_strstatus()`. Test signals are compile coverage across JR, QI2, RNG, and key-generation users and correct behavior for MDHA versus non-MDHA algtype masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/error.h -->
