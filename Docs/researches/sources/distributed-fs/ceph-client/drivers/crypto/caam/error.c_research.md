<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/error.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/error.c

Purpose: central CAAM error reporting and global hardware-format state. It decodes JR/QI/DECO/CCB status words into kernel logs and negative errno values, exports scatterlist debug dumping, and owns global endian/pointer/SoC flags.

Important APIs and control flow: `caam_dump_sg()` hex-dumps scatterlists under DEBUG and is a no-op otherwise. Globals `caam_little_end`, `caam_imx`, and `caam_ptr_sz` are exported and initialized elsewhere. Static tables map descriptor errors, QI errors, CHA IDs, CCB error IDs, and RNG-specific errors to text. `report_ccb_status()` returns `-EBADMSG` for ICV check failures without noisy logs, otherwise ratelimits detailed logs. `report_deco_status()` and `report_qi_status()` decode descriptor/QI errors. `caam_strstatus()` dispatches based on status source and returns negative errno.

State and persistence behavior: exported globals are process-wide CAAM hardware format state; static decode tables are immutable. Error reporting has no per-device persistence beyond log side effects.

Dependencies and integration points: called by JR callbacks, RNG/PRNG, key generation, and QI2 paths through `caam_jr_strstatus()`/`caam_qi2_strstatus()` macros. Uses register status bit definitions from `regs.h` and descriptor constants from `desc.h`.

Risks and test signals: risks include singleton endian/pointer state, `qi_v2` currently unused in dispatch, some source reporters unimplemented, possible out-of-range `err_id_list` indexing for unexpected CCB err IDs, and sensitive data in DEBUG dumps. Test signals include correct errno mapping for ICV failures, readable logs for injected descriptor/CCB/QI errors, no crashes on unknown status values, and correct global initialization before descriptor construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/error.c -->
