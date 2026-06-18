# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc.c

Purpose: defines the generic NAND ECC engine abstraction, default OOB layouts, device-tree ECC configuration parsing, request tweaking helpers, software engine lookup, and on-host hardware engine registry.

Important APIs and types: exported front-door APIs are `nand_ecc_init_ctx()`, `nand_ecc_cleanup_ctx()`, `nand_ecc_prepare_io_req()`, and `nand_ecc_finish_io_req()`. Layout exports include `nand_get_small_page_ooblayout()`, `nand_get_large_page_ooblayout()`, and `nand_get_large_page_hamming_ooblayout()`. Configuration and registry APIs include `of_get_nand_ecc_user_config()`, `nand_ecc_is_strong_enough()`, request tweak helpers, software/on-die/on-host getters, hardware engine register/unregister, put, and `nand_ecc_get_engine_dev()`.

Control flow: the prepare/finish wrappers call engine hooks when present. OOB layout helpers describe legacy small-page, large-page, and large-page Hamming ECC/free regions. OF parsing recognizes no-ECC, software ECC, on-die self phandle, on-host phandle, placement, algorithm, step size, strength, and maximize-strength flags. Strength validation compares correction density and absolute strength against chip requirements. Request tweaking expands partial data/OOB I/O into full-page bounce buffers so ECC engines can operate over whole pages, then restores read data or original request metadata. On-host engines register in a mutex-protected global list and are matched by device pointer from `nand-ecc-engine` phandles.

State and persistence: runtime state includes per-device ECC context, temporary bounce buffers, and the global list of registered on-host engines. Persistent state is only the OOB layout and ECC bytes produced by concrete engines.

Dependencies and integration points: central integration point for NAND core, software BCH/Hamming engines, on-die engines supplied by chips, on-host platform engines such as MXIC and Realtek, MTD OOB APIs, platform OF lookup, and device references.

Risks and test signals: risks include OF phandle reference handling, duplicate hardware registration races, partial-request bounce correctness, OOB layout edge cases, and weak-ECC comparison math. Tests should cover all engine types, invalid strings, missing/probe-deferred phandles, software algo defaults, OOB layout regions for 8/16/64/128-byte OOB, request tweak read/write restore paths, engine device indirection, and register/unregister idempotence.
