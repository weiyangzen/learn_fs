# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_mpc.c

## Purpose

`qeth_core_mpc.c` supplies static MPC/IPA protocol templates and human-readable IPA diagnostics for the qeth core. It is data-oriented: immutable byte arrays provide the base frames for IDX activation, CM enable/setup, ULP enable/setup, DM activation, and IPA PDU headers; lookup tables map IPA command/return-code pairs to stable messages used by debug logging.

## Important APIs and data

- Exported command templates: `IDX_ACTIVATE_READ`, `IDX_ACTIVATE_WRITE`, `CM_ENABLE`, `CM_SETUP`, `ULP_ENABLE`, `ULP_SETUP`, `DM_ACT`, and `IPA_PDU_HEADER`.
- Return-code message tables: default IPA messages plus command-specific maps for adapter parameters, diagnostic assist, create/destroy address, VNICC, bridgeport IQD/OSA, MAC operations, IP/multicast operations, LAN state, VLAN, and routing.
- `qeth_get_ipa_msg(enum qeth_ipa_cmds cmd, enum qeth_ipa_return_codes rc)` first checks the command-specific table, then falls back to the default table, and finally returns the default unknown-error string.
- `qeth_get_ipa_cmd_name(enum qeth_ipa_cmds cmd)` maps IPA command numbers to compact names used in debug output.

## Control flow and integration

The byte-array templates are copied by `qeth_core_main.c` into command buffers and then patched with runtime tokens, device addresses, sequence numbers, protocol types, lengths, and port numbers before the CCW is issued. The return-code helpers are called when IPA replies arrive, especially through `qeth_issue_ipa_msg()`, so hardware status can be logged as meaningful text rather than raw numeric codes.

This file has no complex runtime control flow beyond table lookup. The message mapping order matters: command-specific meanings override generic return-code meanings, because some numeric return codes are reused by different IPA command families.

## State and persistence behavior

There is no mutable persistent state. All templates and lookup tables are static constants in kernel text/rodata. Runtime state is created elsewhere by copying and patching these templates into `struct qeth_cmd_buffer` instances.

## Dependencies and integration points

The file includes `linux/module.h`, `asm/cio.h`, and `qeth_core_mpc.h`. Its constants are consumed by the MPC and IPA setup paths in `qeth_core_main.c`; its string helpers support qeth debug facility logging. The contents must stay synchronized with the packed structures, offsets, sizes, and enum values in `qeth_core_mpc.h`.

## Risks and edge cases

- The templates are opaque hardware frames. A single byte, size constant, or offset mismatch can break device bring-up.
- Return-code values are reused across command families; placing a code in the wrong table can produce misleading diagnostics.
- `qeth_get_ipa_cmd_name()` depends on the final `IPA_CMD_UNKNOWN` entry as fallback by iterating to `ARRAY_SIZE(...) - 1`.
- Adding a new IPA command in the header without updating the command-name or return-code map reduces observability and can hide hardware-specific failures.

## Test signals

Relevant signals include successful MPC initialization through all template-backed commands, correct debug messages for known and unknown IPA return codes, command-name fallback for unknown commands, and compile-time consistency with `qeth_core_mpc.h` enum names and template size macros. Hardware or emulator tests that exercise negative IPA replies are especially useful because they validate command-specific message precedence.
