# subset-b-008329 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/ssl.rs -->
## sources/security-integrity/encfs/src/crypto/ssl.rs

Purpose: implements the central EncFS cryptographic wrapper, `SslCipher`. It provides legacy EncFS-compatible key derivation, volume-key wrapping, filename encryption, file header encryption, per-block encryption/decryption, optional AES-GCM-SIV authenticated block operations, and encrypted xattr name/value helpers.

Important APIs and types: `LegacyCipherKind` selects AES-128/AES-192/AES-256 or Blowfish; `NameEncoding` selects stream or block filename mode; `SslCipher` stores the selected interface, IV length, key material, master IV, and filename mode. Public APIs include `new`, `set_name_encoding`, `set_key`, `derive_key`, `derive_key_legacy`, `derive_key_argon2id`, `encrypt_key`/`decrypt_key`, `encrypt_filename`/`decrypt_filename`, `encrypt_header`/`decrypt_header`, `encrypt_block_inplace`/`legacy_decrypt_block_inplace`, AES-GCM-SIV block helpers, MAC helpers, and xattr encrypt/decrypt helpers. `Drop` zeroizes the resident key and IV buffers.

Control flow: construction maps config interface name and key size into a cipher kind and IV length. KDF functions derive user-key blobs with PBKDF2-HMAC-SHA1, the legacy SHA1 BytesToKey-style loop, or Argon2id. Volume-key wrapping prefixes a 32-bit folded HMAC checksum, then applies the two-pass EncFS stream transform; unwrap reverses the stream transform and verifies the checksum. Stream filename mode stores a 16-bit MAC plus CFB-encrypted name bytes, while block filename mode pads to cipher block size, MACs plaintext plus padding, CBC-encrypts the block payload, and custom-base64 encodes the result. IV derivation uses HMAC(key, master IV || little-endian seed) for interface major >= 3 and an older arithmetic XOR scheme otherwise. File content chooses CBC for full logical blocks and CFB stream encoding for partial blocks; AES-GCM-SIV mode derives deterministic nonce/AAD from file IV and block number and returns or verifies a 16-byte tag.

State and persistence behavior: the cipher is mostly stateless after initialization except for resident volume key and IV. Persisted artifacts produced here include encrypted config `key_data`, encrypted filename strings, encrypted file headers that contain per-file IVs, encrypted data blocks, optional AES-GCM-SIV tags managed by the file codec layer, and encrypted xattrs stored by `fs.rs`. Headerless files use the caller's file IV semantics, while headered files store a random 64-bit file IV encrypted with an external IV, often derived from path IV in paranoia mode.

Dependencies and integration points: depends on RustCrypto AES, Blowfish, CBC, CFB, HMAC, SHA1, PBKDF2, Argon2, AES-GCM-SIV, `getrandom`, `zeroize`, and translated error text. It is consumed by `config` for password verification and cipher setup, `crypto::file`/`crypto::block` for file data codecs, `fs.rs` for live FUSE operations, `encfsctl.rs` for CLI decode/export/cat/password flows, and `reverse_fs` for reverse-mode encrypted views.

Risks: most legacy modes intentionally preserve EncFS behavior, including SHA1-based derivation/MAC folding, 16-bit filename MACs, unauthenticated CBC/CFB content encryption, and compatibility-sensitive endian details. `decrypt_xattr_data` decrypts and checks padding before MAC verification, so malformed encrypted xattrs can expose different error paths. AES-GCM-SIV is limited to 128-bit and 256-bit AES keys; AES-192 configs remain legacy-only. Any change to shuffle/flip, custom base64, MAC folding, or IV endianness would break compatibility with existing volumes. Error messages may leak whether padding, MAC, or tag verification failed.

Test signals: embedded tests cover legacy IV derivation, stream and block round trips across AES and Blowfish, xattr name/value round trips and tamper failure, Argon2id determinism and parameter sensitivity, PBKDF2 and MAC known vectors, little-endian IV derivation guardrails, key-wrap known vectors, filename/header/full-block/partial-block known vectors, and header/content compatibility behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/ssl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/encfsctl.rs -->
## sources/security-integrity/encfs/src/encfsctl.rs

Purpose: implements the `encfsctl` administrative CLI. It inspects configs, rotates passwords, creates new V7 volumes, decodes/encodes paths, lists and cats encrypted content without mounting, scans for cruft, exports plaintext trees, and supports scripted password changes.

Important APIs and types: `Cli` and `Command` define Clap subcommands `Info`, `Passwd`, `Showcruft`, `Decode`, `Encode`, `Cat`, `Ls`, `Autopasswd`, `Export`, and `New`. Key functions are `cmd_info`, `cmd_passwd`, `calibrate_argon2_time_cost`, `cmd_showcruft`, `cmd_decode`, `cmd_encode`, `cmd_cat`, `cmd_ls`, `cmd_autopasswd`, `cmd_new`, `cmd_export`, `export_directory`, path encode/decode helpers, `ensure_v7_compatible`, `format_v7_config_raw`, config discovery helpers, password helpers, and file/path resolution helpers. `ShowcruftStats` tracks scan counters.

Control flow: `main` initializes locale, parses the subcommand, and dispatches to command handlers. Most commands find the newest supported config file, load it through `config::EncfsConfig`, obtain a password interactively or from an external command, derive an `SslCipher`, then perform path or content operations. Password rotation decrypts the current volume key, zeroizes the old password, gathers and verifies a new password, regenerates salt, optionally upgrades to Argon2id and V7, calibrates Argon2 time cost, rewrites key data, saves the config, and backs up the old config after V7 upgrade. `cat`, `ls`, and `export` resolve encrypted paths with filename IV chaining, decrypt file headers when present, and stream content via `FileDecoder`. `export_directory` recurses through the encrypted tree, decrypting filenames, files, permissions, directories, and symlink targets.

State and persistence behavior: reads operate directly against the encrypted root without mounting. Mutating commands update config files: `passwd`/`autopasswd` rewrite key data and salt, `passwd --upgrade` may create `.encfs7` and rename the old config to `.bak`, and `new` creates a fresh `.encfs7` plus random salt and volume key. Export persists plaintext copies under a destination directory and attempts to preserve permissions. The command zeroizes password strings after deriving ciphers or rewriting keys, but volume-key blobs and derived key blobs are ordinary vectors.

Dependencies and integration points: depends on Clap, `rust_i18n`, `rpassword`, `getrandom`, `zeroize`, shell `sh -c` for extpass, `config`, `constants`, `SslCipher`, `FileDecoder`, and Unix path byte conversions. It shares filename/path IV rules with `fs.rs`, shares file content codec parameters with the mounted filesystem, and exposes V7 protobuf formatting through `config_proto`.

Risks: `--extpass` runs through the shell, so command strings are powerful and must be treated as trusted input. Several paths require encrypted names to be UTF-8 strings even though plaintext output may be arbitrary bytes. Export defaults to warning and continuing, which can silently produce partial exports unless `--fail-on-error` is used. Password upgrade writes the new V7 config before renaming the old config, so a failure in the final rename can leave both files. `calibrate_argon2_time_cost` performs a simple one-shot estimate and can divide by a very small elapsed time on extremely fast runs. Direct `cat --ignore-mac` can bypass file-block authentication checks where supported.

Test signals: the embedded test constructs a temporary encrypted symlink and verifies export decrypts the symlink target correctly. Other command behavior is indirectly covered by `config`, `SslCipher`, `FileDecoder`, and filesystem tests, but the broad CLI command matrix, migration failure paths, and export error modes have limited direct test coverage in this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/encfsctl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/encfsr.rs -->
## sources/security-integrity/encfs/src/encfsr.rs

Purpose: implements the `encfsr` reverse-mode CLI, mounting a plaintext source directory as a virtual encrypted EncFS view. It is intended for deterministic encrypted backup/export workflows using V7 configs.

Important APIs and types: `Args` defines positional `config`, `source`, and `mount_point` plus `--stdinpass`, `--extpass`, `--foreground`, and trailing FUSE options. `main` is the only runtime function beyond translated help helpers. It validates inputs, loads config, derives a cipher, builds `reverse_fs::ReverseFs`, and mounts it through `fuse_mt`.

Control flow: startup hardens the process, initializes locale and logging, validates that the source exists and is a directory, validates that the config exists and is a regular file, then loads `EncfsConfig`. It rejects non-V7 configs because reverse mode exposes the config as `.encfs7` inside the virtual filesystem. Password acquisition mirrors the main mount binary: external shell command with `RootDir`, stdin, or interactive prompt. After `config.get_cipher`, the password is zeroized. It rejects `unique_iv = true` because reverse mode requires deterministic, headerless encrypted output. It then reads config bytes and metadata, constructs `ReverseFs`, prepends read-only and default-permissions FUSE options, appends user trailing options, and mounts.

State and persistence behavior: `encfsr` does not mutate the source directory or config file during normal startup. It reads plaintext source data on demand through `ReverseFs` and presents encrypted names/content virtually. The mounted FUSE layer is forced read-only at kernel option level. Config bytes and metadata are retained in memory so the reverse filesystem can expose the config file.

Dependencies and integration points: depends on Clap, `rust_i18n`, `env_logger`, `rpassword`, `zeroize`, shell `sh -c` for extpass, `config`, `security::harden_process`, `reverse_fs::ReverseFs`, and `fuse_mt`. It shares password/cipher derivation with the normal mount path but delegates all reverse filesystem semantics to `reverse_fs`.

Risks: all hard failures print an error and call `std::process::exit(1)` rather than returning structured errors, which is fine for a CLI but harder to unit-test. `--extpass` executes through the shell and is trusted. Reverse mode rejects `unique_iv = true`, so many normal EncFS configs cannot be mounted until created or migrated with compatible settings. User-supplied trailing FUSE options are appended after `ro` and `default_permissions`; depending on FUSE parsing, conflicting options may still affect behavior.

Test signals: no embedded tests in this file. Coverage is expected from `reverse_fs` tests, config loading tests, and manual CLI/FUSE integration tests. Startup validation paths, FUSE option composition, and V7/unique-IV rejection are not directly unit-tested here.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/encfsr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/fs.rs -->
## sources/security-integrity/encfs/src/fs.rs

Purpose: implements the mounted EncFS FUSE filesystem. It maps plaintext FUSE paths and operations to encrypted backing paths, decrypts directory entries and symlinks, translates logical file sizes to encrypted physical sizes, encrypts/decrypts file data through `FileEncoder`/`FileDecoder`, handles metadata operations, and encrypts xattrs.

Important APIs and types: `FileHandle` stores an open backing `File` plus decrypted file IV; `PathInfo` carries logical path, physical path, and path IV for recursive rename/copy operations; `EncFs` stores the encrypted root, `SslCipher`, open-handle map, next handle counter, and loaded config. Key methods include `new`, `encrypt_path`, `decrypt_path`, `rename_internal`, `copy_recursive`, `copy_file_with_header_rewrite`, permission/ownership helpers, truncate helpers, and the full `FilesystemMT` implementation for statfs, chmod, chown, access, truncate, utimens, readlink, link, symlink, getattr, readdir, open, read, release, write, create, unlink, mkdir, mknod, rmdir, rename, and xattr operations.

Control flow: path-facing FUSE methods call `encrypt_path`, which encrypts each component and advances the directory IV when chained-name IV is enabled. `readdir` reverses this process for backing directory entries and skips dot-prefixed config/control files. `open` and `create` open backing files, derive or generate the file IV from encrypted headers or headerless external-IV rules, and cache `FileHandle`s under integer FUSE handles. `read` and `write` wrap the backing file with `FileDecoder` or `FileEncoder` using the cached file IV. `truncate` computes current logical size from physical size, then either writes encrypted zeroes or adjusts physical length on expansion and carefully rewrites partial final blocks on shrink. Rename falls back to recursive copy plus delete when chained-name or external IV rules mean a plain backing rename would make child names, file headers, or symlink targets undecryptable.

State and persistence behavior: persistent state lives in the encrypted backing directory: encrypted filenames, encrypted file headers, encrypted content blocks, encrypted symlink targets, encrypted xattrs under `user.encfs.*`, and Unix metadata. In-memory state is limited to open handles and the next handle counter. File creation writes an encrypted header when config requires one; headerless configurations derive file IV from external path IV when enabled. Recursive rename under external IV chaining rewrites file headers while leaving encrypted bodies intact. Xattr methods encrypt the requested xattr name and value with path IV and store only the encrypted/base64 name on disk.

Dependencies and integration points: depends on `fuse_mt`, `libc`, `log`, Unix metadata and xattr APIs, Base64, `SslCipher`, `BlockLayout`, `FileEncoder`, `FileDecoder`, and `EncfsConfig` codec parameters. It is created by `main.rs`, shares path and content behavior with `encfsctl` utilities, and relies on crypto/file modules for block MAC and AES-GCM-SIV handling.

Risks: this is the highest blast-radius file because it couples cryptography, path mapping, persistence, and POSIX behavior. Open handles cache file IVs; renames or external modifications while handles are live can create semantic edge cases. Recursive rename/copy is not crash-atomic and may leave partial destinations if interrupted. `copy_recursive` skips undecryptable children, which is safer for availability but can drop corrupt or unexpected backing entries during renames. Only the primary gid is considered in `access`; supplementary groups are ignored. Several xattr paths expose different failures for base64, padding, or MAC problems. Hard links are denied under external IV chaining, but allowed otherwise, so sharing encrypted content between different logical paths must still respect IV/header constraints.

Test signals: embedded tests cover `headerless_file_iv` behavior for headerless versus headered files. Broader filesystem behavior is indirectly tested through `lib.rs` fixture tests, `encfsctl` symlink export testing, and crypto/file codec tests, but most FUSE operations, recursive rename crash windows, xattr behavior, permission edge cases, and live-handle interactions need integration-level coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/lib.rs -->
## sources/security-integrity/encfs/src/lib.rs

Purpose: defines the public library facade for the EncFS crate and centralizes locale initialization. It exposes configuration parsing, constants, crypto, mounted filesystem, reverse filesystem, and process-hardening modules to the binaries and tests.

Important APIs and types: public modules are `config`, `config_binary`, `config_proto`, `constants`, `crypto`, `fs`, `reverse_fs`, and `security`. The main function is `init_locale`, which reads `LANG`, strips encoding suffixes, converts POSIX underscores to BCP-47-style hyphens, and calls `rust_i18n::set_locale`.

Control flow: the module declarations make implementation modules available to `main.rs`, `encfsctl.rs`, `encfsr.rs`, and integration consumers. `init_locale` is called by binaries before translated help/errors are needed; if `LANG` is absent it leaves the rust-i18n fallback in place. Tests load fixtures, construct configs/ciphers, decrypt known filenames and file content, and exercise paranoia-mode path IV behavior through `EncFs::decrypt_path`.

State and persistence behavior: the library facade has no persistent state. `init_locale` mutates rust-i18n global locale state for the current process. The embedded tests read fixture configs and encrypted files from `tests/fixtures` but do not modify them.

Dependencies and integration points: depends directly on `rust_i18n` and, in tests, SHA1, Unix `FileExt`, config loading, filesystem path decryption, and file decoding. It is the import surface used by all three binaries: normal mount uses `config` and `fs::EncFs`, control utility uses `config`, `constants`, and `crypto::ssl`, and reverse mount uses `config`, `reverse_fs`, and `security`.

Risks: locale normalization is simple and assumes `LANG` is enough; unsupported locale keys fall back according to rust-i18n behavior. Because many modules are publicly exported, internal APIs may become de facto external contracts. Fixture tests panic if test fixtures are missing, which is acceptable for local tests but not a graceful skip.

Test signals: `test_decrypt_filenames` verifies a V6 fixture config decrypts a known filename and file content hash. `test_paranoia_mode` verifies chained path IV decryption, nonzero path IV, header decryption with external IV, and the same plaintext SHA1 for paranoia-mode content.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/main.rs -->
## sources/security-integrity/encfs/src/main.rs

Purpose: implements the normal `encfs` mount binary. It parses mount options, finds and loads an EncFS config, obtains the password, derives the cipher, optionally daemonizes, constructs `EncFs`, and mounts it with selected FUSE options.

Important APIs and types: `Args` defines `--foreground`, `--verbose`, `-d` debug mode, `-s` single-thread mode, `--public`, `--extpass`, `--stdinpass`, `--read-only`, `--no-default-permissions`, and positional `root`/`mount_point`. `main` handles all runtime behavior. Translated help helper functions supply Clap strings.

Control flow: startup hardens the process, initializes locale, parses CLI args, configures logging, and searches the encrypted root for `.encfs7`, `.encfs6.xml`, then `.encfs5`. It loads `EncfsConfig`, acquires the password from an external shell command, stdin, or prompt, calls `config.get_cipher`, and zeroizes the password. On success it daemonizes unless foreground/debug is active, constructs `EncFs::new`, builds FUSE options for `allow_other`, `default_permissions`, and `ro`, selects the FUSE worker count, and calls `fuse_mt::mount`. On cipher failure it logs and returns the underlying error.

State and persistence behavior: `main.rs` itself does not write config or encrypted data before mounting. After mount, persistence is delegated to `EncFs`. It passes read-only FUSE option when requested but does not otherwise alter the loaded config. The password string is zeroized after cipher derivation.

Dependencies and integration points: depends on Clap, `daemonize`, `env_logger`, `log`, `rust_i18n`, `rpassword`, shell `sh -c` for extpass, `security::harden_process`, `config::EncfsConfig`, `fs::EncFs`, and `fuse_mt`. It is the top-level integration point for `fs.rs` and the config/crypto stack.

Risks: config discovery ignores `.encfs4` and `.encfs3` even though `encfsctl` can detect them, so behavior differs between mount and utility. `--extpass` uses the shell and is trusted input. Daemonization happens after password verification but before FUSE mount, so foreground diagnostics differ from daemon diagnostics. `--public` can add `allow_other`; security then depends on system FUSE policy and the selected `default_permissions` behavior. There is no support for arbitrary trailing FUSE options in this binary.

Test signals: no embedded tests in this file. Behavior is covered indirectly by tests of `config`, `SslCipher`, and `EncFs`, while full CLI option parsing, daemonization, config search precedence, and FUSE mount option composition require integration or manual tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/main.rs -->
