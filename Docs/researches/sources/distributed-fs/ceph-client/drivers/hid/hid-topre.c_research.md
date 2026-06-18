# sources/distributed-fs/ceph-client/drivers/hid/hid-topre.c

Purpose: fixes report descriptors for Topre REALFORCE R2/R3S keyboard non-boot interfaces that claim array input but actually send variable input.

Important APIs, types, and functions: `topre_report_fixup()` is the driver hook. It checks for two known descriptor layouts by size and byte pattern, logs a fixup message, and changes the input item flag from `0x00` to `0x02`. `topre_id_table[]` matches REALFORCE R2 108-key, R2 87-key, and R3S 87-key USB IDs.

Control flow: HID core calls `report_fixup` before parsing. If a known descriptor byte sequence is present at the expected offset, the descriptor is modified in place and returned. Otherwise the original descriptor is returned unchanged.

State and persistence: stateless; no allocations, drvdata, probe, or remove. The only state is the modified in-memory descriptor during HID enumeration.

Dependencies and integration: integrates with HID report fixup and USB device ID matching from `hid-ids.h`.

Risks: offset-based descriptor patching is intentionally narrow; descriptor revisions with shifted bytes may not be fixed. Incorrectly matching a descriptor could change keyboard semantics, but the byte-pattern guards reduce that risk.

Test signals: no automated tests. Hardware validation should confirm the affected keyboard interface emits key events correctly after descriptor parsing and that unaffected descriptors are not patched.
