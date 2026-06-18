# sources/distributed-fs/ceph-client/arch/alpha/lib/callback_srm.S

## Purpose
Assembly wrappers for SRM console callback functions and SRM fixup dispatch, with generic fallback stubs when SRM is unavailable. The source was read as part of `subset-b-000628` and contains 109 lines.

## Important APIs, Types, and Functions
Defines `srm_fixup`, `callback_puts`, `callback_open`, `callback_close`, `callback_read`, `callback_open_console`, `callback_close_console`, `callback_getenv`, `callback_setenv`, `callback_getc`, `callback_reset_term`, `callback_term_int`, `callback_term_ctl`, `callback_process_keycode`, `callback_ioctl`, `callback_write`, `callback_reset_env`, `callback_save_env`, `callback_pswitch`, and `callback_bios_emul`. Exports `callback_getenv`, `callback_setenv`, and `callback_save_env`; weakly defines `alpha_using_srm` and `callback_init_done` defaults.

## Control Flow
Callbacks load the kernel GP, optionally reject non-SRM generic boots, locate the HWRPB console callback routine block, shift Linux arguments to the VMS calling convention, extract callback code and argument count from wrapper data, and jump to the SRM dispatch procedure. Non-SRM builds return `-1` immediately.

## State and Persistence Behavior
State is read from HWRPB/CRB fields, `alpha_using_srm`, and callback initialization flags. SRM callbacks may mutate firmware environment variables or console state; this wrapper itself stores only weak default data.

## Dependencies
Depends on `asm/console.h` callback codes, `hwrpb`, Alpha GP/procedure descriptor conventions, SRM firmware, and generic-kernel `alpha_using_srm` detection.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Argument shifting and VMS descriptor use are ABI-critical. Calling SRM on non-SRM firmware must return safely. Environment-setting callbacks are persistent firmware operations, so wrong codes or counts can corrupt SRM variables.

## Test Signals
Build SRM and generic Alpha configs, call getenv/setenv/save-env paths on SRM hardware, verify non-SRM stubs return `-1`, and test early console callbacks before and after callback initialization.
