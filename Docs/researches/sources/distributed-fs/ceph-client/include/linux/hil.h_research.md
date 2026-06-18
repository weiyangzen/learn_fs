# sources/distributed-fs/ceph-client/include/linux/hil.h

## Purpose
`hil.h` defines Hewlett Packard Human Interface Loop protocol constants, packet layout, command codes, response decoding macros, locale names, keyboard translation tables, and poll record flags. It supports legacy HP-HIL input devices such as keyboards, mice, tablets, and other loop peripherals.

## Important APIs, Types, And Functions
`typedef u32 hil_packet` is the canonical packet representation. The file defines wire bit positions, packet bit masks, error/control bits, loop command enum values, device ID and describe-record masks, macros such as `HIL_IDD_LEN()`, `HIL_IDD_AXIS_MAX()`, `HIL_IDD_NUM_BUTTONS()`, `HIL_EXD_LEN()`, and `HIL_EXD_LOCALE()`, plus `HIL_LOCALE_MAP`, `HIL_KEYCODES_SET1`, `HIL_KEYCODES_SET3`, and `HIL_POL_*` poll flags.

## Control Flow And State
HIL controller and input drivers send commands, receive response records, decode device capabilities with IDD/EXD macros, map keyboard packets through static key tables, and interpret poll records for axes, buttons, character sets, status, and flow control. Loop state is external to this header and stored in HIL MLC/controller code.

## Dependencies And Integration Points
It includes architecture integer types and uses Linux input key codes in keycode tables, so implementation files must include input definitions appropriately. It integrates with `hil_mlc.h`, HP SDC MLC drivers, serio devices, and input subsystem device registration.

## Risks
Macros assume packet arrays in exact receive order and can read incorrect offsets if callers do not validate response lengths. `HIL_IDD_NUM_PROMPTS()` references `HIL_IDD_IOD_NPROMPT_MASK`, while the defined mask is `HIL_IDD_IOD_PROMPT_MASK`, so code paths using that macro may fail to compile or rely on an external definition. Legacy timing constants and raw packet bits are hardware-sensitive.

## Test Signals
Test HP-HIL autoconfiguration, IDD/EXD parsing, keyboard keycode translation, relative and absolute pointer reports, locale handling, malformed short records, loop error flags, and poll records with status pending or CTS set.
