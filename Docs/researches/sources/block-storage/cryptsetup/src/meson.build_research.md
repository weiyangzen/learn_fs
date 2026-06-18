# File Research: sources/block-storage/cryptsetup/src/meson.build

## Purpose
Meson build definition for cryptsetup-family command-line executables and SSH token helper source grouping.

## Build Targets
- `cryptsetup` is built when `get_option('cryptsetup')` is enabled.
- `veritysetup` is built when `get_option('veritysetup')` is enabled.
- `integritysetup` is built when `get_option('integritysetup')` is enabled.

## cryptsetup Sources
Includes `cryptsetup.c`, common arg/blockdev/LUKS/password/progress/tools helpers, reencryption helpers, key description, keyslot check, and `lib_tools_files`.

## veritysetup Sources
Includes `veritysetup.c`, `utils_args.c`, `utils_tools.c`, and `lib_tools_files`.

## integritysetup Sources
Includes `integritysetup.c`, `utils_args.c`, `utils_blockdev.c`, `utils_progress.c`, `utils_tools.c`, and `lib_tools_files`.

## Dependencies
- `cryptsetup`: `popt`, `pwquality`, `passwdqc`, `uuid`, `blkid`.
- `veritysetup`: `popt`, `blkid`.
- `integritysetup`: `popt`, `uuid`, `blkid`.
- All three link with `libcryptsetup`, use common link args and tool include directories, and install into `sbindir`.

## Notes
`src_ssh_token_files` is defined for SSH token support and includes `utils_password.c` and `utils_tools.c`.
