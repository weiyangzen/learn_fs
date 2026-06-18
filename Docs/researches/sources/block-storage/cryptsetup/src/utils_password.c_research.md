# File Research: sources/block-storage/cryptsetup/src/utils_password.c

## Purpose
Password/passphrase and keyfile input handling, including optional password quality checks through pwquality or passwdqc.

## Password Quality
- If built with pwquality, `tools_check_pwquality()` loads default settings/config and validates the password.
- If built with passwdqc, `tools_check_passwdqc()` loads passwdqc config and validates.
- If neither is enabled, quality checking is a no-op.
- `tools_check_password()` selects the compiled backend.

## Terminal Input
- `interactive_pass()` opens `/dev/tty` when available, disables echo with termios, writes the prompt, reads with optional timeout, restores terminal state, and prints a newline.
- `crypt_get_key_tty()` allocates safe buffers, reads the passphrase, optionally verifies by asking twice, and returns the passphrase length.
- Reads stop at newline or max interactive length; reaching max length logs a trimming warning.

## Main Key Input API
`tools_get_key()`:
- Temporarily unblocks signals if needed.
- For stdin on a tty, prompts interactively and rejects keyfile offsets.
- For stdin not on a tty, reads binary input through `crypt_keyfile_device_read`; absent `key_file` enables EOL stop behavior.
- For file input, reads through `crypt_keyfile_device_read`.
- Runs password quality only for passphrase input, not keyfile input.
- Uses cryptsetup device names or loop backing files in generated prompts.

## Diagnostics
`tools_passphrase_msg()` maps common unlock errors to user-facing messages:
- `-EPERM`: no key available with this passphrase.
- `-ENOENT`: no usable keyslot.

## Notes
All password buffers use `crypt_safe_alloc`/`crypt_safe_free` so secrets are wiped on free.
