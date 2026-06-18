# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-leash.h

## Purpose

This header declares dynamic bindings for the MIT Leash Windows DLL (`leashw32.dll` or `leashw64.dll`). It exposes interactive credential acquisition, password change, credential listing/destruction, import/renewal, and Leash default preference APIs to OpenAFS Windows code.

## Important APIs, Types, and Functions

- `LEASH_DLL` selects `leashw64.dll` on `_WIN64`, otherwise `leashw32.dll`.
- Dialog/UI APIs: `Leash_kinit_dlg`, `Leash_kinit_dlg_ex`, `Leash_changepwd_dlg`, and `Leash_changepwd_dlg_ex`.
- Credential lifecycle APIs: `Leash_kinit`, `Leash_kinit_ex`, `Leash_klist`, `Leash_kdestroy`, `Leash_renew`, `Leash_import`, and `Leash_importable`.
- Password and error helpers: `Leash_checkpwd`, `Leash_changepwd`, `Leash_get_lsh_errno`, `Leash_set_help_file`, `Leash_get_help_file`, and `Leash_timesync`.
- Defaults and policy knobs include get/set/reset triplets for lifetime, renew-till, forwardable, no-addresses, proxiable, public IP, KRB4 usage, min/max life and renewal bounds, renewable, lock-file locations, uppercase realm, MSLSA import, and preserve-kinit-settings.
- `Leash_reset_defaults` resets Leash preference defaults.

## Control Flow

This file only declares function-pointer types. A caller loads `LEASH_DLL`, resolves the symbols into `pLeash_*` function pointers, then drives either UI flows or noninteractive credential operations through those pointers. Defaults are read, modified, or reset one option at a time.

## State and Persistence Behavior

The external Leash DLL owns persistent defaults, ticket cache changes, import state, help file path, last Leash error, and renewal behavior. The header only defines the bindings. Many default setters appear to persist user or machine preference state through Leash/KFW configuration mechanisms.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and `<leashwin.h>` for `LPLSH_DLGINFO`, `LPLSH_DLGINFO_EX`, and `TICKETINFO`. It integrates OpenAFS Windows user workflows with Kerberos credential acquisition and Leash preference management.

## Risks

- UI dialog functions require valid `HWND` ownership and should run on an appropriate UI thread.
- `char *` password/principal buffers carry sensitive data; callers must manage lifetime, encoding, and clearing.
- Default setters can persist configuration changes with broad user-visible impact.
- KRB4-related defaults are compatibility-sensitive and may be ignored or unsupported by modern Leash builds.
- The trailing comment says not all functions are present, so consumers should expect an incomplete binding surface.

## Test Signals

Loader tests should assert DLL name selection by architecture and expected symbol availability for supported Leash versions. UI tests should isolate dialog entry points behind mocks or manual harnesses. Preference tests should verify get/set/reset round trips in a disposable profile or registry hive.
