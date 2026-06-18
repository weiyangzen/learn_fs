# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks-secvar.c

Purpose: Adapts PowerVM PLPKS objects into the kernel secure-variable (`secvar`) interface for static and dynamic secure boot key management.

Important APIs/types/functions: Defines secure variable name lists, `get_policy()`, `plpks_get_variable()`, `plpks_set_variable()`, `plpks_get_sb_keymgmt_mode()`, `plpks_secvar_format()`, `plpks_max_size()`, and static/dynamic `secvar_operations`.

Control flow: Init checks PLPKS availability, reads firmware variable `SB_VERSION` to determine static versus dynamic key-management mode, and installs the matching secvar ops. Gets convert UTF-8 names to little-endian UTF-16 PLPKS labels, read OS-owned variables, and report sizes. Sets parse an 8-byte big-endian flags prefix, strip it from payload, choose policy by variable name, and issue a signed update.

State and persistence: No local cache is kept. Secure variables and `SB_VERSION` persist in PLPKS/firmware; secvar ops expose those values to the broader secure-boot stack.

Dependencies and integration points: Depends on `plpks.c` read/signed-update APIs, `asm/secvar.h`, UTF-8/UTF-16 conversion helpers, pseries initcalls, and secure boot variable naming conventions.

Risks: Name conversion length excludes the terminating nul and must match PLPKS label semantics. Write payloads must include signed-update flags and at least one byte of real data. Returning `-EIO` for most read failures hides detail from userspace intentionally, while writes preserve PLPKS-specific errors.

Test signals: Static and dynamic key mode detection, reads of PK/KEK/db/dbx/grubdb/sbat variables, signed updates with invalid flags or short buffers, missing `SB_VERSION`, PLPKS unavailable boot, and secvar format/max-size queries.

Source read size: 224 lines, 6481 bytes.
