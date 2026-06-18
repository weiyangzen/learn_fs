<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/pam_ecryptfs.c -->
# sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/pam_ecryptfs.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/pam_ecryptfs.c_research.md`. Source lines read for this pass: 546.

## Purpose
PAM module that loads eCryptfs authentication tokens into the user's session keyring, mounts the user's private directory on session open, unmounts it on close, and rewraps the wrapped mount passphrase when the login password changes.

## Important APIs, Types, And Functions
Exports PAM entry points `pam_sm_authenticate`, `pam_sm_setcred`, `pam_sm_open_session`, `pam_sm_close_session`, and `pam_sm_chauthtok`. Important helpers are `file_exists_dotecryptfs`, `wrap_passphrase_if_necessary`, `fetch_pwd`, and `private_dir`.

## Control Flow
`pam_sm_authenticate` resolves the PAM user, temporarily drops effective credentials to the user, checks `~/.ecryptfs/auto-mount`, skips key loading if already mounted, obtains either `PAM_AUTHTOK` or an independent wrapping passphrase, forks, validates the keyring, and inserts either a raw passphrase token or an unwrapped `wrapped-passphrase` token. Session hooks fork and exec `/sbin/mount.ecryptfs_private` or `/sbin/umount.ecryptfs_private` as the user. `pam_sm_chauthtok` uses old and new PAM tokens to unwrap and rewrap the stored mount passphrase.

## State And Persistence Behavior
Reads and writes `~/.ecryptfs/auto-mount`, `auto-umount`, `wrapping-independent`, `Private.sig`, `wrapped-passphrase`, and `/dev/shm/.ecryptfs-$USER` bootstrap passphrase files. Persists key material only through libecryptfs wrapped-passphrase routines and kernel keyring insertion; it also creates update-notifier marker links for passphrase recording reminders.

## Dependencies And Integration Points
Depends on Linux PAM, libc passwd/group APIs, syslog, setuid/setgid/setgroups, libecryptfs keyring/wrapping APIs, `/sbin/mount.ecryptfs_private`, `/sbin/umount.ecryptfs_private`, and the eCryptfs per-user dotfile layout.

## Risks And Edge Cases
The module handles secrets and privilege transitions; child exit statuses are mostly ignored and PAM often returns success after logging failures. `/dev/shm` bootstrap wrapping, auto-mount markers, and independent wrapping prompts must preserve ownership and mode checks. Any change to UID/GID restoration can break login sessions or leak keys.

## Test Signals
Covered indirectly by private setup/mount scripts and kernel integration tests that require keys, mounts, and unmounts. Manual PAM testing should verify login, logout, password-change rewrap, independent wrapping, and encrypted-home bootstrap paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/pam_ecryptfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/python/__init__.py -->
# sources/security-integrity/ecryptfs-utils/src/python/__init__.py

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/python/__init__.py_research.md`. Source lines read for this pass: 0.

## Purpose
Empty package marker for the legacy Python eCryptfs API package.

## Important APIs, Types, And Functions
Exports no names and performs no initialization.

## Control Flow
Importing the package executes no statements; consumers import `ecryptfsapi.py` for actual helpers.

## State And Persistence Behavior
No state, persistence, IO, or side effects.

## Dependencies And Integration Points
Only Python package import mechanics.

## Risks And Edge Cases
Compatibility risk is packaging related: removing or renaming it can break imports that expect `src/python` to be a package.

## Test Signals
Import smoke tests are sufficient; no behavioral unit test is required for this zero-byte marker.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/python/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/python/ecryptfsapi.py -->
# sources/security-integrity/ecryptfs-utils/src/python/ecryptfsapi.py

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/python/ecryptfsapi.py_research.md`. Source lines read for this pass: 82.

## Purpose
Legacy Python 2 convenience API for toggling eCryptfs private-directory automount/autounmount, invoking mount and unmount helpers, and checking whether setup is needed.

## Important APIs, Types, And Functions
Module constants name `~/.ecryptfs/auto-mount`, `auto-umount`, `Private.mnt`, and derived `PRIVATE_LOCATION`. Functions include `set_automount`, `get_automount`, `set_autounmount`, `get_autounmount`, `set_mounted`, `get_mounted`, and `needs_setup`.

## Control Flow
Setter functions build shell commands (`touch`, `rm`, `/sbin/mount.ecryptfs_private`, `/sbin/umount.ecryptfs_private`) and run them with `commands.getstatusoutput`. Getter functions use `os.path.exists` or scan `/proc/mounts` for `Private.mnt`.

## State And Persistence Behavior
Persists user preferences by creating or removing files in `~/.ecryptfs`; mount state is external in `/proc/mounts` and the eCryptfs helper.

## Dependencies And Integration Points
Depends on Python 2 `commands`, `os`, user home expansion, `/proc/mounts`, and setuid private mount helpers.

## Risks And Edge Cases
Shell command construction is unquoted, Python 2-only, and uses import-time `PRIVATE_LOCATION`, so changes after import are not seen. `needs_setup` has an unimplemented encrypted-home check.

## Test Signals
Test signals are simple file toggle checks plus helper invocation smoke tests under a configured eCryptfs user.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/python/ecryptfsapi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/utils/Makefile.am

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/Makefile.am_research.md`. Source lines read for this pass: 72.

## Purpose
Automake build/install manifest for eCryptfs command-line utilities, setuid-root sbin helpers, shell scripts, optional TPM key generation, and the small internal test program.

## Important APIs, Types, And Functions
Defines `rootsbin_PROGRAMS`, `bin_PROGRAMS`, `bin_SCRIPTS`, `noinst_PROGRAMS`, source lists, CFLAGS, LDADD dependencies, `EXTRA_DIST`, and an `install-exec-hook` that links `umount.ecryptfs_private` to `mount.ecryptfs_private`.

## Control Flow
Automake consumes the declarations to compile helpers against `libecryptfs`, keyutils, libgcrypt, and optionally TSPI. Install phase places root sbin helpers and user scripts in the expected locations.

## State And Persistence Behavior
No runtime state, but it controls installed filesystem layout and therefore PAM/script integration paths.

## Dependencies And Integration Points
Integrates with the top-level autotools build, `src/libecryptfs/libecryptfs.la`, keyutils, libgcrypt, TSPI, and generated `config.h`.

## Risks And Edge Cases
Incorrect install destinations or missing LDADD entries break PAM/session paths. The hardlink/symlink relation between mount and unmount private helper is behaviorally significant because mode is selected by argv[0].

## Test Signals
`make`, `make install`, and `ENABLE_TESTS` exercise compilation of the listed binaries; packaging tests should verify installed modes and paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok.c_research.md`. Source lines read for this pass: 149.

## Purpose
Debugging support for printing an `ecryptfs_auth_tok` structure and its nested password/private-key/session-key fields.

## Important APIs, Types, And Functions
Defines `PRINT`, `dump_hex`, and `dump_auth_tok`; it reads `struct ecryptfs_auth_tok`, `struct ecryptfs_password`, and eCryptfs flag constants.

## Control Flow
`dump_auth_tok` switches on token type, prints password or private-key metadata, then prints session-key flags and encrypted/decrypted key buffers when present. `dump_hex` formats bytes as dotted hex with line breaks.

## State And Persistence Behavior
No persistence, but it emits sensitive in-memory token data to stdout or syslog depending on `USE_PRINTF`.

## Dependencies And Integration Points
Depends on eCryptfs public headers and either stdio or syslog.

## Risks And Edge Cases
The file is intentionally unsafe for production diagnostics because it can print passphrases and key material. Fixed-size local formatting buffers rely on callers providing bounded sizes.

## Test Signals
Useful only in debug builds or manual token inspection; there is no automated test in this subset.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok_key.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok_key.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok_key.c_research.md`. Source lines read for this pass: 49.

## Purpose
Small diagnostic entry point for dumping an auth token stored in the kernel keyring by numeric key id.

## Important APIs, Types, And Functions
Defines `main`, calls `keyctl(KEYCTL_READ, key_id, ...)`, and delegates decoded printing to `dump_auth_tok` from `dump_auth_tok.c`.

## Control Flow
Parses one key-id argument with `atoi`, reads a raw `struct ecryptfs_auth_tok` payload from that key, prints a success line, and dumps the decoded token fields.

## State And Persistence Behavior
Reads keyring state only; produces diagnostic output that can contain secret key material.

## Dependencies And Integration Points
Depends on keyutils, libecryptfs token layout, and a readable eCryptfs key id in the current keyring.

## Risks And Edge Cases
Sensitive output and keyring permission assumptions are the main risks. The `atoi` parse gives weak validation, and the include name is the legacy `keyutil.h` form.

## Test Signals
Manual test requires inserting a known auth token, passing its key id, and confirming the expected fields are decoded.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-find -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-find

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-find_research.md`. Source lines read for this pass: 59.

## Purpose
Shell utility that maps between encrypted and decrypted eCryptfs pathnames by using inode numbers across current eCryptfs mounts.

## Important APIs, Types, And Functions
No functions; command-line argument `$1`, `/proc/mounts`, `ls -aid`, `awk`, and `find -inum` are the operative interfaces.

## Control Flow
Validates the supplied path, infers encrypt or decrypt direction by whether the name contains `ECRYPTFS_FNEK_ENCRYPTED.`, collects readable eCryptfs lower or upper paths from `/proc/mounts`, then searches each candidate tree for the same inode number.

## State And Persistence Behavior
Reads current mount table and directory trees; does not persist changes.

## Dependencies And Integration Points
Depends on Linux `/proc/mounts`, shell, `ls`, `awk`, and `find`; requires execute/read access to relevant lower or upper trees.

## Risks And Edge Cases
Inode matching can be slow on large trees and can produce ambiguous results across mounts or reused inodes. Parsing `/proc/mounts` by whitespace is fragile for escaped paths.

## Test Signals
Test by creating a file in an eCryptfs mount, locating its lower encrypted path, and verifying the tool maps both directions.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-find -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-migrate-home -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-migrate-home

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-migrate-home_research.md`. Source lines read for this pass: 206.

## Purpose
Root-only migration script that converts an existing user home into an encrypted eCryptfs home by moving the cleartext tree aside, bootstrapping eCryptfs configuration, copying data back through the encrypted mount, and leaving recovery instructions.

## Important APIs, Types, And Functions
Shell functions `usage`, `error`, `warning`, `info`, `assert_dir_empty`, `get_user_home`, `sanity_check`, and `encrypt_dir`; CLI accepts `-u|--user`.

## Control Flow
Validates root privileges, gets the target home from passwd, checks that eCryptfs state does not already exist, requires `rsync` and `lsof`, checks 2.5x free space, ensures destination directories are empty, moves the original home to `/home/$USER.XXXXXXXX`, runs `ecryptfs-setup-private -b`, rsyncs data into the new encrypted home, unmounts it, and prints mandatory login/backup notes.

## State And Persistence Behavior
Creates `/home/.ecryptfs/$USER`, symlinks in the user home via setup-private, a temporary cleartext backup home, and encrypted home contents.

## Dependencies And Integration Points
Depends on root, `getent`, `du`, `df`, `rsync`, `lsof`, `mktemp`, `ecryptfs-setup-private`, `umount`, and conventional `/home` layout.

## Risks And Edge Cases
High blast radius: moving homes and rsyncing data can lock users out or lose data if interrupted. Unquoted passphrase forwarding in setup arguments and open-file/disk-space checks deserve caution.

## Test Signals
Best tested in a disposable VM with a throwaway user, confirming login before reboot and verifying the cleartext backup can restore the original home.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-migrate-home -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-mount-private -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-mount-private

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-mount-private_research.md`. Source lines read for this pass: 81.

## Purpose
Interactive shell wrapper for mounting a user's configured private directory when the required mount key is not already in the keyring.

## Important APIs, Types, And Functions
Uses `~/.ecryptfs/wrapping-independent`, `wrapped-passphrase`, `Private.sig`, `ecryptfs-unwrap-passphrase`, `ecryptfs-add-passphrase`, `ecryptfs-insert-wrapped-passphrase-into-keyring`, and `/sbin/mount.ecryptfs_private`.

## Control Flow
First silently tries `/sbin/mount.ecryptfs_private`. If that fails and config files exist, prompts up to three times for the login or independent wrapping passphrase, inserts the FEK or FEK/FNEK keys, then invokes the setuid mount helper.

## State And Persistence Behavior
Reads per-user dotfiles and modifies only kernel keyring/mount state. It may print a current-shell directory refresh hint if `$PWD` is the mounted directory.

## Dependencies And Integration Points
Depends on shell, stty, gettext, head, wc, configured eCryptfs files, and installed helper binaries.

## Risks And Edge Cases
Passphrase handling through pipelines is sensitive; stdin mode must preserve NUL/newline behavior. The one-line versus two-line signature file controls whether filename encryption key insertion is attempted.

## Test Signals
Covered by setup-private's mount/write/umount/read sanity flow and manual login/private-directory mount tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-mount-private -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-recover-private -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-recover-private

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-recover-private_research.md`. Source lines read for this pass: 120.

## Purpose
Root-only recovery helper that discovers `.Private` directories and mounts them read-only by default using either the wrapped passphrase or the recorded mount passphrase.

## Important APIs, Types, And Functions
Shell functions `error` and `info`; CLI accepts optional `--rw` and optional target directories.

## Control Flow
Requires root, discovers candidate directories by arguments or `find / -type d -name .Private`, prompts per candidate, detects filename encryption, inserts keys from `wrapped-passphrase` or direct mount passphrase, builds eCryptfs mount options, validates keys with `keyctl`, creates `/tmp/ecryptfs.XXXXXXXX`, and mounts with `mount -i -t ecryptfs`.

## State And Persistence Behavior
Creates temporary recovery mountpoints and inserts keys into the user keyring; does not alter the encrypted source unless `--rw` is used and the user writes through the mount.

## Dependencies And Integration Points
Depends on root, find, keyctl, mount, mktemp, eCryptfs passphrase tools, and the `Private.sig`/`wrapped-passphrase` layout.

## Risks And Edge Cases
`find /` is expensive and noisy; `keyctl` check on an empty FNEK string can be brittle. Recovery mounts should default to read-only to avoid damaging partially recovered data.

## Test Signals
Manual recovery test should use a copied `.Private` tree and both wrapped-passphrase and mount-passphrase paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-recover-private -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-rewrite-file -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-rewrite-file

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-rewrite-file_research.md`. Source lines read for this pass: 75.

## Purpose
Rewrites files, symlinks, or directories in place so eCryptfs re-encrypts contents or filenames under current mount options.

## Important APIs, Types, And Functions
No shell functions beyond `error`; arguments are paths to rewrite. Uses `mktemp`, `cp -a`, and `mv -T`.

## Control Flow
Iterates over paths, skips missing entries and `.`, renames directories through a temporary name, or copies files/symlinks to a temporary peer and renames back over the original. Counts successful rewrites and exits nonzero if any failed.

## State And Persistence Behavior
Mutates target paths in place and creates temporary peer files/directories. The intended persistent effect is newly encrypted lower contents or filename metadata.

## Dependencies And Integration Points
Depends on shell, gettext, `mktemp`, `cp`, `mv`, and an active eCryptfs mount.

## Risks And Edge Cases
In-place rewrite can lose metadata or data on interruption, especially around copy/rename failures. Directories are renamed rather than deep-copied, so callers must avoid racing users.

## Test Signals
Test by changing eCryptfs options or keys, rewriting representative files/dirs/symlinks, unmounting/remounting, and verifying data and lower-name changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-rewrite-file -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-private -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-private

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-private_research.md`. Source lines read for this pass: 464.

## Purpose
Primary setup script for per-user `~/Private` encrypted directories and encrypted-home bootstrap configuration.

## Important APIs, Types, And Functions
Shell functions include `usage`, `undo_msg`, `error`, `error_testing`, `random_passphrase`, and `filename_encryption_available`. CLI controls force, independent wrapping, FNEK, username, login/mount passphrases, automount, bootstrap, and undo instructions.

## Control Flow
Validates user and group membership, resolves home, creates either home-local or `/home/.ecryptfs/$USER` layout, checks for existing config and active mounts, prompts/verifies login and mount passphrases, creates `~/.Private` and mountpoint, writes automount flags and wrapping mode, wraps or temporarily stores the mount passphrase, inserts keys, writes `Private.sig` and `Private.mnt`, then runs a mount/write/umount/read sanity test unless bootstrapping.

## State And Persistence Behavior
Persists `wrapped-passphrase`, `Private.sig`, `Private.mnt`, `auto-mount`, `auto-umount`, `wrapping-independent`, symlinks, and encrypted data directories. Bootstrap may leave `/dev/shm/.ecryptfs-$USER` until PAM wraps it on password setup.

## Dependencies And Integration Points
Depends on unix_chkpwd, libecryptfs command-line tools, `/sbin/mount.ecryptfs_private`, `/sbin/umount.ecryptfs_private`, sysfs version detection, restorecon when present, and standard shell utilities.

## Risks And Edge Cases
This script owns long-lived secret and mount metadata. Argument passphrases are visible to process listings, bootstrap temporarily stores a mount passphrase protected by file mode, and failure handling must keep config files consistent.

## Test Signals
Contains its own mount/write/umount/read checksum test. Additional signals are `ecryptfs-verify`, login automount, logout unmount, and FNEK/no-FNEK setup variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-private -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-swap -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-swap

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-swap_research.md`. Source lines read for this pass: 181.

## Purpose
Root helper that converts existing swap devices to encrypted cryptsetup-backed swap to prevent cleartext private data from leaking through swap.

## Important APIs, Types, And Functions
Shell functions `error`, `info`, `warn`, and `usage`; CLI accepts `-f|--force` and `-n|--no-reload`.

## Control Flow
Requires cryptsetup and root, discovers active swap devices, skips non-swap/RAM/already-encrypted/already-configured swaps, warns about breaking hibernate unless forced, comments out original fstab entries, appends `cryptswapN` entries to `/etc/crypttab` and `/etc/fstab`, then optionally restarts cryptdisks and swaps.

## State And Persistence Behavior
Mutates `/etc/fstab`, `/etc/crypttab`, active swap state, and device mapper mappings.

## Dependencies And Integration Points
Depends on `/proc/swaps`, blkid, dmsetup, sed, cryptsetup, initramfs-tools paths, `/etc/init.d/cryptdisks`, swapoff, and swapon.

## Risks And Edge Cases
System-level configuration edits can break boot, hibernate/resume, or swap availability. It appends entries without transactional rollback.

## Test Signals
Requires VM-level integration tests that inspect fstab/crypttab changes and reboot/swap activation behavior; do not run on shared developer machines.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-swap -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-stat.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-stat.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-stat.c_research.md`. Source lines read for this pass: 75.

## Purpose
User utility that prints eCryptfs metadata/stat information for a supplied file using libecryptfs helpers.

## Important APIs, Types, And Functions
Defines `usage` and `main`; uses `struct ecryptfs_crypt_stat_user` and `ecryptfs_parse_stat` from the eCryptfs headers/library.

## Control Flow
Validates one filename argument, opens it read-only, reads up to 4096 bytes, parses eCryptfs metadata from that buffer, and prints file version, decrypted size, header bytes, metadata location, encrypted/plaintext flag, and HMAC flag.

## State And Persistence Behavior
Read-only against the target file; output is diagnostic text.

## Dependencies And Integration Points
Depends on `src/libecryptfs/libecryptfs.la`, generated config, stdio, and file metadata/header bytes that exist on eCryptfs encrypted files.

## Risks And Edge Cases
Behavior depends on whether the input includes readable eCryptfs metadata in the first page. Parse failure is reported as 'metadata not found' but returns success after printing the message.

## Test Signals
Use encrypted and plaintext/non-eCryptfs files to verify parsed metadata fields and graceful metadata-not-found behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-umount-private -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-umount-private

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-umount-private_research.md`. Source lines read for this pass: 26.

## Purpose
Shell wrapper that unmounts the user's private directory and removes corresponding FEK/FNEK keys from the user keyring.

## Important APIs, Types, And Functions
Uses `/sbin/umount.ecryptfs_private`, `~/.ecryptfs/Private.sig`, `keyctl list @u`, and `keyctl unlink`.

## Control Flow
Detects whether `$PWD` is the private mount, invokes the setuid unmount helper, then iterates signatures in `Private.sig` and unlinks matching user keys. It prints a current-shell refresh hint if relevant.

## State And Persistence Behavior
Changes mount state and keyring state; reads per-user signature file.

## Dependencies And Integration Points
Depends on grep, keyctl, awk, gettext, and the private unmount helper.

## Risks And Edge Cases
Signature matching by grep suffix can unlink unexpected matching keys if key descriptions collide. Missing signature files can make key cleanup incomplete.

## Test Signals
Mount a private directory, run wrapper, confirm `/proc/mounts` no longer lists it and `keyctl list @u` no longer contains its signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-umount-private -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-verify -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-verify

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-verify_research.md`. Source lines read for this pass: 245.

## Purpose
Validation script for checking whether a user's encrypted home/private setup and filename-encryption mode match expected configuration.

## Important APIs, Types, And Functions
Functions include `ecryptfs_exists`, `sigfile_valid`, `mountfile_valid`, `automount_true`, `owns_mountpoint`, `mount_is_home`, `mount_is_private`, `filenames_encrypted`, and `filenames_not_encrypted`. CLI options are additive.

## Control Flow
Parses requested checks and optional `--user`, resolves home, then executes each check. Any failure prints an error and exits nonzero; all checks passing prints configuration valid.

## State And Persistence Behavior
Read-only over passwd data, `~/.ecryptfs`, `Private.sig`, `Private.mnt`, mountpoint ownership, and automount flags.

## Dependencies And Integration Points
Depends on shell, gettext, getent, stat, wc, and the standard eCryptfs per-user layout.

## Risks And Edge Cases
Assumes fixed file names and one/two-line signature semantics. It checks configuration, not whether keys are available or mounts are currently usable.

## Test Signals
Use after setup-private and encrypted-home bootstrap with `--home`, `--private`, `--filenames-encrypted`, and `--filenames-not-encrypted` combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-verify -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_key.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_key.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_key.c_research.md`. Source lines read for this pass: 34.

## Purpose
Skeleton utility intended to add a public-key module auth token to the user session keyring.

## Important APIs, Types, And Functions
Defines `usage` and `main`; calls `ecryptfs_add_key_module_key_to_keyring` with a `struct ecryptfs_pki_elem *` placeholder.

## Control Flow
Requires exactly one argument, but the argument is not used to select or configure a key module. It attempts insertion with `selected_pki == NULL`, prints inserted signature on success, or libecryptfs errors on failure.

## State And Persistence Behavior
May insert a key into the session keyring if libecryptfs accepts the placeholder; otherwise only prints diagnostics.

## Dependencies And Integration Points
Depends on libecryptfs public-key module APIs.

## Risks And Edge Cases
Appears incomplete: no key-module selection or parameter parsing is implemented despite usage text. Passing NULL into library code is a likely failure or compatibility hazard.

## Test Signals
A useful test would prove whether any module can be inserted; current behavior should be treated as negative/incomplete.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_passphrase.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_passphrase.c_research.md`. Source lines read for this pass: 124.

## Purpose
CLI utility that reads a passphrase and inserts a password auth token into the user session keyring, optionally also adding a filename-encryption key.

## Important APIs, Types, And Functions
Defines `usage` and `main`; calls `ecryptfs_get_passphrase`, `ecryptfs_get_version`, `ecryptfs_supports_filename_encryption`, `ecryptfs_read_salt_hex_from_rc`, and `ecryptfs_add_passphrase_key_to_keyring`.

## Control Flow
Supports interactive or stdin passphrase input and optional `--fnek`. It validates length, checks kernel FNEK support if requested, reads configured salt or defaults, inserts the FEK auth token, and for `--fnek` inserts a second token with the FNEK salt.

## State And Persistence Behavior
Changes kernel user/session keyring state and prints inserted signatures; reads eCryptfs rc salt.

## Dependencies And Integration Points
Depends on libecryptfs, kernel keyring support, and eCryptfs kernel version reporting.

## Risks And Edge Cases
Passphrases can flow through stdin pipelines. FNEK mode depends on kernel feature detection; failure after FEK insertion but before FNEK insertion can leave partial state.

## Test Signals
Used heavily by setup/mount scripts. Test with stdin and interactive modes, `--fnek`, invalid passphrase lengths, and keyctl signature lookup.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_passphrase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_generate_tpm_key.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_generate_tpm_key.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_generate_tpm_key.c_research.md`. Source lines read for this pass: 262.

## Purpose
Optional TSPI utility that creates a TPM storage key bound to selected current PCR values and registers it in persistent storage.

## Important APIs, Types, And Functions
Functions `usage`, `util_bytes_to_string`, and `main`; TSPI calls include context creation/connection, TPM object lookup, PCR reads, PCR composite setup, SRK load, policy secret setup, RSA key creation, random UUID generation, and key registration.

## Control Flow
Parses repeated `-p PCR` options, queries the TPM PCR count, validates selected PCRs, reads their current values into a PCR composite, loads the SRK with the well-known secret, creates a 2048-bit volatile non-migratable storage key, registers it under a random UUID, and prints selected PCR values and UUID.

## State And Persistence Behavior
Writes a key into TSPI user persistent storage and allocates/frees TPM context memory.

## Dependencies And Integration Points
Built only with `BUILD_TSPI`; depends on TrouSerS/TSPI headers and libraries and an accessible TPM.

## Risks And Edge Cases
Legacy TPM 1.2 assumptions, well-known SRK secret, PCR off-by-one validation (`>` rather than `>=`) risk, and sparse memory cleanup on error paths.

## Test Signals
Requires TPM/TSPI integration hardware or emulator; verify PCR-bound key registration and reported UUID can be used by the key module.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_generate_tpm_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_insert_wrapped_passphrase_into_keyring.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_insert_wrapped_passphrase_into_keyring.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_insert_wrapped_passphrase_into_keyring.c_research.md`. Source lines read for this pass: 98.

## Purpose
Unwraps a stored wrapped-passphrase file with a wrapping passphrase and inserts the resulting eCryptfs auth token into the user session keyring.

## Important APIs, Types, And Functions
Defines `usage` and `main`; calls `ecryptfs_get_wrapped_passphrase_filename`, `ecryptfs_get_passphrase`, `ecryptfs_read_salt_hex_from_rc`, and `ecryptfs_insert_wrapped_passphrase_into_keyring`.

## Control Flow
Supports default file interactive mode, explicit file interactive mode, stdin passphrase mode, and direct argument passphrase mode. It validates passphrase length, selects configured/default salt, calls libecryptfs to unwrap and insert, and prints the signature.

## State And Persistence Behavior
Reads a wrapped-passphrase file and writes to the kernel keyring; no file mutation.

## Dependencies And Integration Points
Depends on libecryptfs, configured per-user wrapped-passphrase path, and keyring support.

## Risks And Edge Cases
Direct argument mode exposes passphrases in process listings. This tool is central to private mount login behavior, so salt handling must match the wrapping path exactly.

## Test Signals
Setup-private and mount-private exercise it. Unit coverage should include default path, explicit path, stdin, bad passphrase, and missing file.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_insert_wrapped_passphrase_into_keyring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_rewrap_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_rewrap_passphrase.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_rewrap_passphrase.c_research.md`. Source lines read for this pass: 108.

## Purpose
Changes the wrapping passphrase protecting an existing eCryptfs wrapped mount passphrase.

## Important APIs, Types, And Functions
Defines `usage` and `main`; uses `ecryptfs_get_passphrase`, `ecryptfs_unwrap_passphrase`, `ecryptfs_wrap_passphrase`, and salt loading.

## Control Flow
Reads old and new wrapping passphrases interactively, from stdin, or from argv. Interactive mode requires new passphrase confirmation. It unwraps the mount passphrase with the old wrapping passphrase, then writes the same mount passphrase rewrapped with the new wrapping passphrase.

## State And Persistence Behavior
Overwrites the wrapped-passphrase file. The unwrapped mount passphrase lives transiently in stack memory.

## Dependencies And Integration Points
Depends on libecryptfs wrapping APIs and configured salt semantics.

## Risks And Edge Cases
Argument mode exposes secrets. There is no explicit secure zeroing of stack passphrase after use, and interruption while writing could corrupt the wrapped file depending on libecryptfs behavior.

## Test Signals
Test by wrapping a known mount passphrase, rewrapping, proving old password no longer unwraps and new password does.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_rewrap_passphrase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_unwrap_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_unwrap_passphrase.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_unwrap_passphrase.c_research.md`. Source lines read for this pass: 94.

## Purpose
Prints the unwrapped mount passphrase from a wrapped-passphrase file after receiving the wrapping passphrase.

## Important APIs, Types, And Functions
Defines `usage` and `main`; uses default wrapped-passphrase filename, `ecryptfs_get_passphrase`, salt loading, and `ecryptfs_unwrap_passphrase`.

## Control Flow
Supports default or explicit file, interactive or stdin/direct wrapping passphrase. It validates length, unwraps into a fixed-size buffer, and writes the plaintext mount passphrase to stdout.

## State And Persistence Behavior
Read-only on wrapped-passphrase file; exposes secret output intentionally for backup/recovery.

## Dependencies And Integration Points
Depends on libecryptfs and matching salt configuration.

## Risks And Edge Cases
Plaintext mount passphrase is emitted to stdout and may be captured in shell history, logs, pipes, or terminals. Direct argument mode exposes wrapping passphrase.

## Test Signals
Setup-private instructions rely on this. Test success, wrong passphrase, stdin mode, and default path resolution.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_unwrap_passphrase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_wrap_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_wrap_passphrase.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_wrap_passphrase.c_research.md`. Source lines read for this pass: 97.

## Purpose
Creates or replaces an eCryptfs wrapped-passphrase file from a mount passphrase and wrapping passphrase.

## Important APIs, Types, And Functions
Defines `usage` and `main`; uses `ecryptfs_get_passphrase`, salt loading, and `ecryptfs_wrap_passphrase`.

## Control Flow
Accepts file path and passphrases interactively, via stdin, or via argv. It validates passphrase lengths, reads configured/default salt, and delegates file serialization/encryption to libecryptfs.

## State And Persistence Behavior
Writes the wrapped-passphrase file, usually under `~/.ecryptfs/wrapped-passphrase`.

## Dependencies And Integration Points
Depends on libecryptfs wrapping APIs and filesystem permissions around the target file.

## Risks And Edge Cases
Argument mode exposes both secrets. Callers must set restrictive umask/mode because this file protects access to encrypted data.

## Test Signals
Used by setup-private. Round-trip test with unwrap and insert-wrapped-passphrase into keyring is the key signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_wrap_passphrase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/gen_key.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/gen_key.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/gen_key.c_research.md`. Source lines read for this pass: 181.

## Purpose
Legacy helper code for public/private key generation directory setup; the main key generation routine is currently stubbed out.

## Important APIs, Types, And Functions
Defines `ecryptfs_generate_key` returning `-EINVAL`, plus `create_subdirectory` and `create_default_dir` for `~/.ecryptfs/pki/<module>` paths.

## Control Flow
The disabled block shows intended decision-graph/key-module selection. Active code only creates default PKI directories and subdirectories from slash-separated relative file paths.

## State And Persistence Behavior
Can create `~/.ecryptfs`, `~/.ecryptfs/pki`, and `~/.ecryptfs/pki/<alias>` with mode 0700 via helper calls.

## Dependencies And Integration Points
Depends on `struct ecryptfs_key_mod`, passwd/home information from callers, mkdir, and eCryptfs headers.

## Risks And Edge Cases
`create_subdirectory` mutates the input string in place while walking slashes and has limited cleanup on allocation errors. The exported generate function is nonfunctional.

## Test Signals
Directory creation helpers should be tested with nested relative names, existing directories, and invalid permissions. `ecryptfs_generate_key` should currently be expected to fail.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/gen_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/io.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/io.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/io.c_research.md`. Source lines read for this pass: 293.

## Purpose
Shared interactive I/O and menu helpers for mount and manager utilities.

## Important APIs, Types, And Functions
Functions include `mygetchar`, `get_string_stdin`, `get_string`, `manager_menu`, `read_passphrase_salt`, and `ecryptfs_select_key_mod`; private helpers disable/restore terminal echo.

## Control Flow
Input helpers read from stdin with CR-to-LF normalization and optional echo disabling. `read_passphrase_salt` prompts twice for a mount passphrase and zeroes the confirmation buffer. Menu helpers validate numeric choices and key-module selections.

## State And Persistence Behavior
No persisted state; temporarily changes terminal attributes and stores secrets in heap/stack buffers.

## Dependencies And Integration Points
Depends on termios, stdio, errno, mlock, libecryptfs constants, and key-module list structures.

## Risks And Edge Cases
Terminal echo must be restored on all paths; some buffers are not mlocked or securely cleared. Dynamic stdin reading doubles buffers and must preserve NUL termination.

## Test Signals
Interactive tests should cover EOF, long input, echo on/off, invalid menu selections, and passphrase mismatch.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/io.h -->
# sources/security-integrity/ecryptfs-utils/src/utils/io.h

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/io.h_research.md`. Source lines read for this pass: 32.

## Purpose
Header declaring shared I/O/menu helpers used by eCryptfs utilities.

## Important APIs, Types, And Functions
Declares `main_menu`, `manager_menu`, `read_passphrase_salt`, `get_string_stdin`, `ecryptfs_select_key_mod`, and `mygetchar`.

## Control Flow
No execution; establishes compile-time interface between `io.c`, `mount.ecryptfs.c`, `manager.c`, and related helpers.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Includes `ecryptfs.h` for constants and struct declarations.

## Risks And Edge Cases
Prototype drift from `io.c` would break builds or cause undefined behavior in C89-style callers.

## Test Signals
Compilation of `mount.ecryptfs`, `ecryptfs-manager`, and `test` verifies this header contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/manager.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/manager.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/manager.c_research.md`. Source lines read for this pass: 147.

## Purpose
Interactive key-management menu for adding passphrase/public-key auth tokens or invoking key generation.

## Important APIs, Types, And Functions
Main program uses `manager_menu`, `read_passphrase_salt`, `ecryptfs_validate_keyring`, `ecryptfs_add_passphrase_key_to_keyring`, key-module selection/list APIs, and `ecryptfs_generate_key`.

## Control Flow
Validates keyring integrity, loops over menu selections, adds a passphrase key after prompting, tries public-key module selection/insertion, calls key-generation helper, or exits.

## State And Persistence Behavior
Writes auth tokens to the kernel keyring; otherwise only interactive terminal state.

## Dependencies And Integration Points
Depends on keyutils, libecryptfs, io helpers, decision graph/key module structures, and libgcrypt/key module build dependencies.

## Risks And Edge Cases
Some public-key generation paths are incomplete because `gen_key.c` is stubbed. Interactive secret handling has the same terminal and memory risks as `io.c`.

## Test Signals
Manual test the menu under a working keyring; passphrase insertion can be validated with `keyctl list @u`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs.c_research.md`. Source lines read for this pass: 662.

## Purpose
General eCryptfs mount helper used by `/bin/mount` to gather/validate mount options, manage signature cache warnings, and invoke the real mount command.

## Important APIs, Types, And Functions
Important functions: `parse_arguments`, `strip_userland_opts`, `process_sig`, `opts_str_contains_option`, `ecryptfs_validate_mount_opts`, `ecryptfs_mount`, `ecryptfs_do_mount`, and `main`.

## Control Flow
Locks future memory, validates user and keyring, parses source/target/options, toggles verbosity/signature-cache behavior, runs `ecryptfs_process_decision_graph` unless remounting, appends `ecryptfs_unlink_sigs`, prompts about unknown signatures, validates required `ecryptfs_key_bytes`, canonicalizes paths, and forks `/bin/mount -i --no-canonicalize -t ecryptfs`.

## State And Persistence Behavior
May create `~/.ecryptfs/sig-cache.txt` and append signatures. Mount state is delegated to `/bin/mount` and the kernel.

## Dependencies And Integration Points
Depends on libecryptfs decision graph, keyutils, libgcrypt, sysfs version detection, passwd home lookup, and `/bin/mount`.

## Risks And Edge Cases
Mount option parsing and string scrubbing are security-sensitive. Unknown options intentionally pass through to the kernel, while userland options must not. Signature-cache prompts can block automation unless `no_prompt`/verbosity options are set.

## Test Signals
Exercise interactive and `-o` modes, `no_sig_cache`, `no_prompt`, FNEK options, unknown options, missing key bytes, and remount rejection.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs_private.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs_private.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs_private.c_research.md`. Source lines read for this pass: 716.

## Purpose
Setuid-capable private directory mount/unmount helper that lets non-root users mount configured eCryptfs private directories without fstab entries.

## Important APIs, Types, And Functions
Key helpers: `read_config`, `check_username`, `fetch_sig`, `check_ownership_mnt`, `check_ownerships`, `update_mtab`, `lock_counter`, `bump_counter`/`increment`/`decrement`/`zero`, and `main`.

## Control Flow
Drops effective uid to the caller, resolves default `Private` paths or alias `.conf`, locks a per-user counter in `/dev/shm`, validates username and signatures, builds fixed AES/16-byte mount options with FEK/FNEK signatures, chdirs into and canonicalizes the mountpoint, then either regains root to `mount()` or decrements session count, removes keys, and execs `/bin/umount -i -l .`.

## State And Persistence Behavior
Reads `~/.ecryptfs/<alias>.sig`, optional `<alias>.conf`, and `Private.mnt`; updates `/etc/mtab` when needed; maintains `/dev/shm/ecryptfs-$USER-$alias` session counters; changes keyring and mount state.

## Dependencies And Integration Points
Depends on setuid installation, keyutils, libecryptfs `ecryptfs_private_is_mounted` and key removal, mntent APIs, `/bin/umount`, and strict per-user ownership.

## Risks And Edge Cases
This is a high-risk privilege boundary. Ownership checks, username filtering, alias validation, counter locking, mtab updates, and retained real uid for keyring access are all security critical.

## Test Signals
Private setup scripts exercise normal paths. Additional tests should cover alias config rejection, invalid signatures, non-owned paths, concurrent sessions, forced unmount, mtab symlink behavior, and key cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs_private.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/plaintext_decision_graph.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/plaintext_decision_graph.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/plaintext_decision_graph.c_research.md`. Source lines read for this pass: 43.

## Purpose
Decision-graph node definitions for plaintext/passthrough behavior in the interactive mount option resolver.

## Important APIs, Types, And Functions
Defines `struct param_node plaintext_arr[]` with one mount option name, prompt text, default value, and two yes/no transitions.

## Control Flow
When included in `mount.ecryptfs`, the graph asks whether to enable plaintext passthrough and emits the `passthrough` mount option with value `1` or `0`.

## State And Persistence Behavior
No persistence itself; affects generated mount options.

## Dependencies And Integration Points
Depends on `decision_graph.h` and libecryptfs graph traversal conventions.

## Risks And Edge Cases
Incorrect graph definitions can silently produce insecure mount options such as unintended plaintext passthrough or malformed option names.

## Test Signals
Interactive mount tests should verify user choices map to the expected `ecryptfs_passthrough` option behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/plaintext_decision_graph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/test.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/test.c_research.md`. Source lines read for this pass: 481.

## Purpose
Non-installed C test harness for legacy eCryptfs extent translation, lower-size calculations, simulated page encryption flow, and parsing of `ecryptfsrc` options.

## Important APIs, Types, And Functions
Defines local test structs plus `ecryptfs_extent_to_lwr_pg_idx_and_offset`, `test_extent_translation`, simulated lower-page helpers, `ecryptfs_encrypt_page`, `upper_size_to_lower_size`, `test_upper_size_to_lower_size`, `test_nv_list_from_file`, and `main`.

## Control Flow
Current `main` runs only `test_nv_list_from_file` and jumps to exit, so later extent/encrypt/size tests are unreachable without editing. The simulated encryption path traces lower-page reads/writes rather than performing real crypto.

## State And Persistence Behavior
Reads local `ecryptfsrc`; otherwise allocates/free simulated page state and prints diagnostics.

## Dependencies And Integration Points
Depends on libecryptfs parser `parse_options_file`, C stdlib, and local `io.c` linkage in Makefile.

## Risks And Edge Cases
Because most tests are unreachable, build success does not imply extent translation coverage. This is a developer harness rather than a reliable regression suite.

## Test Signals
To make it useful, remove the early `goto out` or split the option parser test from the extent/size vector tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/umount.ecryptfs.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/umount.ecryptfs.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/umount.ecryptfs.c_research.md`. Source lines read for this pass: 190.

## Purpose
General eCryptfs umount helper that unlinks eCryptfs auth tokens from the keyring before delegating to `/bin/umount -i`.

## Important APIs, Types, And Functions
Functions include `get_mount_opt_value`, `unlink_keys_from_keyring`, `construct_umount_args`, and `main`.

## Control Flow
Looks up the target mountpoint in `/etc/mtab`, checks for `ecryptfs_unlink_sigs`, extracts FEK/FNEK signatures from mount options, removes those auth tokens from the keyring, prepends `-i` to the original umount arguments, and `execv`s `/bin/umount`.

## State And Persistence Behavior
Mutates keyring state; actual unmount and mtab updates are delegated to `/bin/umount`.

## Dependencies And Integration Points
Depends on mntent parsing of `/etc/mtab`, libecryptfs key removal, and `/bin/umount`.

## Risks And Edge Cases
Parsing mount options by substring can mis-handle malformed options. Missing mtab entries or no `ecryptfs_unlink_sigs` skip key cleanup.

## Test Signals
Mount with unlink_sigs, unmount through helper, and verify both mount disappearance and key removal. Also test non-eCryptfs arguments are passed to umount.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/umount.ecryptfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/tests/Makefile.am

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/Makefile.am_research.md`. Source lines read for this pass: 3.

## Purpose
Top-level Automake manifest for the eCryptfs test hierarchy.

## Important APIs, Types, And Functions
Declares `SUBDIRS = lib userspace kernel`, distributes `run_tests.sh`, `new.sh`, and `tests.rc`.

## Control Flow
Automake recurses into library, userspace, and kernel test directories during build/test setup.

## State And Persistence Behavior
No runtime persistence; controls build-system traversal and distributed test metadata.

## Dependencies And Integration Points
Depends on autotools and the subordinate test directories.

## Risks And Edge Cases
Removing a subdirectory here silently drops an entire test lane from recursive builds.

## Test Signals
A recursive `make check` or distribution tarball validation should include the listed subdirectories and scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/Makefile.am

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/Makefile.am_research.md`. Source lines read for this pass: 92.

## Purpose
Automake manifest for kernel-level eCryptfs regression scripts and compiled fixtures.

## Important APIs, Types, And Functions
Lists distributed shell tests in `dist_noinst_SCRIPTS`, compiled fixtures in `noinst_PROGRAMS` under `ENABLE_TESTS`, per-fixture `_SOURCES`, and one libecryptfs-linked miscdev test.

## Control Flow
Builds C fixtures only when tests are enabled and packages the shell wrappers that orchestrate eCryptfs lower/upper mounts.

## State And Persistence Behavior
No runtime state; controls which regression tests are available to the test runner.

## Dependencies And Integration Points
Depends on autotools, C compiler, eCryptfs test helper library, and libecryptfs for miscdev-bad-count.

## Risks And Edge Cases
A missing source mapping means the wrapper may exist without its binary. The manifest also includes tests outside this work item, so edits can affect broader coverage.

## Test Signals
`make check ENABLE_TESTS` should compile all `noinst_PROGRAMS` and make wrappers available.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent.sh_research.md`. Source lines read for this pass: 46.

## Purpose
Kernel regression wrapper that runs the directory-concurrent compiled stress test inside an eCryptfs mount.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is mkdir/rmdir race and hang detection; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent/test.c_research.md`. Source lines read for this pass: 287.

## Purpose
Compiled kernel regression fixture for multi-process mkdir/rmdir stressor.

## Important APIs, Types, And Functions
`hang_check`, `test_dirs`, `test_exercise`, signal handlers, and duration CLI. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
forks workers per CPU; each syscall is wrapped in a child and `select` timeout to detect kernel hangs. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
no persistent state beyond temporary directories; relies on wrapper cleanup; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
mkdir/rmdir syscall latency and deadlock regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/enospc.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/enospc.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/enospc.sh_research.md`. Source lines read for this pass: 53.

## Purpose
Kernel regression wrapper that creates a bounded lower filesystem and runs the ENOSPC compiled writer.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is proper ENOSPC propagation without corruption; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/enospc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/enospc/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/enospc/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/enospc/test.c_research.md`. Source lines read for this pass: 99.

## Purpose
Compiled kernel regression fixture for writer that expects ENOSPC before a requested file size is reached.

## Important APIs, Types, And Functions
`test_exercise`, signal handler, and size CLI. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
creates a file, writes 64 KiB zero buffers until write fails, and passes only when errno is ENOSPC. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
creates and unlinks one test file; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
ENOSPC propagation signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/enospc/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random.sh_research.md`. Source lines read for this pass: 47.

## Purpose
Kernel regression wrapper that runs the random sparse-extension compiled test with a lower maximum size.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is sparse writes, reads, final size, and unlink; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random/test.c_research.md`. Source lines read for this pass: 197.

## Purpose
Compiled kernel regression fixture for random sparse extension read/write verifier.

## Important APIs, Types, And Functions
`test_write`, `test_read`, `test_write_read`, and `test_exercise`. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
writes small buffers at random offsets up to a limit, reads each back, verifies final size, and unlinks. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
one temporary file with sparse extents; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
sparse write/read and size accounting signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/file-concurrent.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/file-concurrent.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/file-concurrent.sh_research.md`. Source lines read for this pass: 46.

## Purpose
Kernel regression wrapper that runs the file-concurrent compiled stress test inside an eCryptfs mount.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is create/truncate/unlink race and hang detection; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/file-concurrent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/file-concurrent/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/file-concurrent/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/file-concurrent/test.c_research.md`. Source lines read for this pass: 331.

## Purpose
Compiled kernel regression fixture for multi-process create/truncate/unlink stressor.

## Important APIs, Types, And Functions
`hang_check`, `test_files`, `test_exercise`, and signal handlers. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
forks CPU-scaled workers that repeatedly create, truncate to several sizes, and unlink files with per-operation timeouts. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
temporary files in the mounted test directory; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
file operation race and hang regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/file-concurrent/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat.sh_research.md`. Source lines read for this pass: 50.

## Purpose
Kernel regression wrapper that runs the root-only inode-size race stat fixture.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is plaintext size visibility after cache drops; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat/test.c_research.md`. Source lines read for this pass: 375.

## Purpose
Compiled kernel regression fixture for root-only inode size race regression for kernel bug 36002.

## Important APIs, Types, And Functions
`drop_cache`, `check_size`, child `do_test`, pipe protocol, and main loop. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
creates/truncates/syncs a file to changing sizes, drops caches, and fans out child stat checks over pipes. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
writes `/proc/sys/vm/drop_caches` and a single test file; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
stale plaintext inode size race signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inotify.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/inotify.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/inotify.sh_research.md`. Source lines read for this pass: 46.

## Purpose
Kernel regression wrapper that runs the inotify compiled event propagation suite.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is IN_* event forwarding from lower/upper eCryptfs operations; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inotify.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inotify/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/inotify/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/inotify/test.c_research.md`. Source lines read for this pass: 651.

## Purpose
Compiled kernel regression fixture for inotify event propagation suite.

## Important APIs, Types, And Functions
`test_inotify`, helpers for access/modify/attrib/create/delete/move/close, and `inotify_test` table. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
sets a watch, performs one filesystem operation, waits with timeout, and verifies expected IN_* flags. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
creates/removes files and directories under a supplied path; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
inotify correctness signal across eCryptfs.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inotify/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/link.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/link.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/link.sh_research.md`. Source lines read for this pass: 83.

## Purpose
Kernel regression wrapper that performs hard-link sanity checks through an eCryptfs mount.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is link count and shared size behavior across remount; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/link.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/llseek.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/llseek.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/llseek.sh_research.md`. Source lines read for this pass: 45.

## Purpose
Kernel regression wrapper that runs the llseek compiled sparse-file semantics test.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is lseek not extending files and holes reading as zero; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/llseek.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/llseek/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/llseek/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/llseek/test.c_research.md`. Source lines read for this pass: 242.

## Purpose
Compiled kernel regression fixture for sparse lseek semantics verifier.

## Important APIs, Types, And Functions
single `main` with open/lseek/write/read/stat checks. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
first confirms lseek past EOF does not extend file, then writes markers around holes and verifies zero-filled holes and final size after reopen. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
creates and unlinks one file; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
sparse-file hole and size regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/llseek/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-1009207.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-1009207.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-1009207.sh_research.md`. Source lines read for this pass: 58.

## Purpose
Kernel regression wrapper that checks default ACL mask behavior under differing umasks.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 1009207 ACL/umask regression; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-1009207.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-469664.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-469664.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-469664.sh_research.md`. Source lines read for this pass: 47.

## Purpose
Kernel regression wrapper that runs `lsattr` on an eCryptfs file.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 469664 ioctl/attribute compatibility; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-469664.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-509180.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-509180.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-509180.sh_research.md`. Source lines read for this pass: 66.

## Purpose
Kernel regression wrapper that modifies the lower encrypted file across unmount/remount with the paired C helper.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 509180 lower-file modification and cache coherency; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-509180.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-509180/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-509180/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-509180/test.c_research.md`. Source lines read for this pass: 124.

## Purpose
Compiled kernel regression fixture for lower-file byte mutator for LP 509180.

## Important APIs, Types, And Functions
single `main` with `-i`/`-d` options and offset constant 9. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
opens the lower encrypted file, reads one byte at offset 9, increments or decrements it, seeks back, and writes it. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
mutates lower file content intentionally; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
lower cache coherency regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-509180/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919.sh_research.md`. Source lines read for this pass: 46.

## Purpose
Kernel regression wrapper that runs the symlink size/readlink C helper.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 524919 symlink target length reporting; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919/test.c_research.md`. Source lines read for this pass: 100.

## Purpose
Compiled kernel regression fixture for symlink readlink/lstat length checker.

## Important APIs, Types, And Functions
single `main` creating a symlink to argv path. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
creates a file and symlink, calls readlink and lstat, and passes if returned target length equals `st_size`. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
creates and removes a file plus symlink; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
symlink metadata size regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-561129.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-561129.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-561129.sh_research.md`. Source lines read for this pass: 62.

## Purpose
Kernel regression wrapper that checks free-inode reporting after moving files into the mount.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 561129 statfs free inode accounting; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-561129.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-613873.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-613873.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-613873.sh_research.md`. Source lines read for this pass: 63.

## Purpose
Kernel regression wrapper that checks mtime changes after chmod on a file.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 613873 metadata timestamp update; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-613873.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-745836.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-745836.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-745836.sh_research.md`. Source lines read for this pass: 57.

## Purpose
Kernel regression wrapper that truncates and removes a file after remount.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 745836 truncate/removal behavior; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-745836.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-870326.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-870326.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-870326.sh_research.md`. Source lines read for this pass: 46.

## Purpose
Kernel regression wrapper that runs the mmap-after-close C helper.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 870326 dirty mmap writeback without kernel log errors; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-870326.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-870326/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-870326/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-870326/test.c_research.md`. Source lines read for this pass: 160.

## Purpose
Compiled kernel regression fixture for mmap-after-close dirty writeback regression.

## Important APIs, Types, And Functions
`klog_read` and `main`. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
creates a file, mmaps it shared, closes fd, captures kernel log, writes through mapping, unmaps, and checks for new error text. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
creates/unlinks a file and reads kernel log via klogctl; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
kernel warning/error regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-870326/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-872905.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-872905.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-872905.sh_research.md`. Source lines read for this pass: 77.

## Purpose
Kernel regression wrapper that fills the lower filesystem and attempts upper creation.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 872905 ENOSPC lower-file size handling; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-872905.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-885744.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-885744.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-885744.sh_research.md`. Source lines read for this pass: 50.

## Purpose
Kernel regression wrapper that creates a long filename in the encrypted mount.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 885744 encrypted filename length handling; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-885744.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-911507.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-911507.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-911507.sh_research.md`. Source lines read for this pass: 78.

## Purpose
Kernel regression wrapper that truncates the lower file after dropping caches and reads through eCryptfs.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 911507 lower-size repair on read; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-911507.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-926292.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-926292.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-926292.sh_research.md`. Source lines read for this pass: 53.

## Purpose
Kernel regression wrapper that uses POSIX ACLs on a directory and checks mode refresh.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 926292 stale directory inode attributes; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-926292.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-994247.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-994247.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-994247.sh_research.md`. Source lines read for this pass: 37.

## Purpose
Kernel regression wrapper that loads eCryptfs and runs the miscdev bad count helper.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is Launchpad 994247 misc device close/count behavior; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-994247.sh -->
