# sources/cloud-native/ostree/src/libotutil/ot-gpg-utils.c

## Purpose
Provides GPGME integration helpers: error translation, temporary homedir/keyring setup, GIO stream adapters for GPGME data, context creation, legacy gpg-agent cleanup, and OpenPGP Web Key Directory URL generation.

## Important APIs, Types, And Functions
Public functions are `ot_gpgme_throw`, `ot_gpgme_ctx_tmp_home_dir`, `ot_gpgme_data_input`, `ot_gpgme_data_output`, `ot_gpgme_new_ctx`, `ot_gpgme_kill_agent`, and `ot_gpg_wkd_urls`. Internal callbacks map GPGME reads/writes/seeks/releases to `GInputStream`/`GOutputStream` and convert `GError` codes back to `errno`. `encode_wkd_local` computes SHA1 of the local email part and zbase32-encodes it.

## Control Flow
`ot_gpgme_throw` maps selected GPGME errors to `G_IO_ERROR` values and prefixes messages. Temporary homedir creation uses `mkdtemp`, configures the GPGME engine homedir, optionally creates `pubring.gpg`, and cleans up on failure. Data wrapper creation installs callback tables and refs the underlying stream until release. Context creation wraps `gpgme_new` and optional homedir selection. Agent cleanup skips GnuPG >= 2.1.17 and otherwise spawns `gpg-connect-agent --homedir ... killagent /bye`. WKD URL generation validates exactly one `@`, lowercases for hashing/domain path, escapes the original local part, and returns advanced/direct URLs.

## State And Persistence Behavior
Creates temporary GPG homedir directories and optional keyring files under the system temp dir. It may spawn and kill gpg-agent processes tied to a homedir. Stream wrappers hold references until GPGME releases them. WKD generation is stateless.

## Dependencies And Integration Points
Depends on GPGME, GIO streams, libglnx, zbase32, GLib checksums, URI escaping, and process spawning. Used by OSTree GPG signature verification and key retrieval flows.

## Risks
Temporary homedirs must be removed by callers after success; this file only cleans up on setup failure. `g_output_stream_flush` is attempted after writes and any flush error causes a write failure. Version parsing for GnuPG assumes at least three dotted components when available. WKD validation is simple and does not fully validate email syntax beyond one `@`.

## Test Signals
Tests should cover GPGME error mapping, temporary homedir cleanup on failure, stream read/write/seek callbacks, non-seekable streams, context homedir selection, agent cleanup command behavior with mocked versions, and WKD URL vectors.
