# subset-b-009571 research

This grouped report covers the subset-b-009571 source files. Each source section is bounded with the reconciliation markers required for splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/setcifsacl.c -->
# sources/user-network-fs/cifs-utils/setcifsacl.c

## Purpose
`setcifsacl.c` implements the `setcifsacl` command, a CIFS/SMB userspace helper that edits NT security descriptors exposed by the Linux CIFS client through extended attributes. It can add, add-and-reorder, delete, modify, or replace DACL/SACL ACEs, and can replace owner or group SIDs. It is intentionally descriptor-component scoped: it modifies one component and preserves the rest.

## Important APIs, types, and functions
The code depends on `cifsacl.h` descriptor structures such as `struct cifs_ntsd`, `struct cifs_ctrl_acl`, `struct cifs_ace`, and `struct cifs_sid`, plus `ace_kinds`. It uses `getxattr`/`setxattr` against `ATTRNAME_ACL`, `ATTRNAME_NTSD`, and `ATTRNAME_NTSD_FULL`; the attribute name selects the kernel CIFS SMB security-info flags. SID parsing is delegated to the idmap plugin through `init_plugin`, `str_to_sid`, and `exit_plugin` when available, with `raw_str_to_sid` as fallback.

Core helpers include `copy_cifs_sid`, `get_cifs_sid_size`, `get_aces_offset`, `get_aces_size`, `get_acl_revision`, `copy_sec_desc`, `copy_sec_desc_with_sid`, `copy_ace`, `compare_aces`, `alloc_sec_desc`, and the operation functions `ace_set`, `ace_add`, `ace_add_reorder`, `ace_modify`, and `ace_delete`. Command parsing is handled by `parse_cmdline_aces`, `build_cmdline_aces`, `verify_ace_type`, `verify_ace_flags`, and `verify_ace_mask`.

## Control flow
`main` parses one action option, optional `-U`, and a target path. For ACE actions it counts and tokenizes comma-separated `ACL:SID:TYPE/FLAGS/MASK` entries, converts SIDs, validates type/flag/mask values, then loops over `getxattr` with increasing buffers until the descriptor fits or `XATTR_SIZE_MAX` is reached. Owner/group changes fetch `system.cifs_ntsd`, rebuild owner/group layout with an unchanged DACL, and write the descriptor. ACE changes fetch either DACL or SACL information, build fetched ACE copies, apply the selected mutation, rebuild descriptor offsets and ACL headers, then call `setxattr`.

## State and persistence
The persistent state is the server-backed NT security descriptor reachable through CIFS xattrs. The utility mutates file metadata on a mounted CIFS share and has no separate local state. It must preserve endian encoding, SID lengths, ACL counts, and descriptor offsets, including Azure-style descriptors where owner/group SIDs can trail ACLs.

## Dependencies and integration points
It integrates with the kernel CIFS client xattr ABI, SMB servers that honor security descriptor updates, and the cifs-utils idmap plugin. It uses libc endian conversion, getopt, xattr APIs, and constants from CIFS ACL headers. Runtime behavior depends heavily on mount options such as `cifsacl` and on the user credentials used for the mounted share.

## Risks
The code performs manual binary layout construction with limited bounds validation. Risks include malformed server descriptors causing offset mistakes, allocation sizes based on simplified maximum ACE sizes, memory leaks in `build_reorder_aces` because only pointer arrays are freed after deep copies, and compatibility issues around SACL writes requiring `system.cifs_ntsd_full`. `verify_ace_type` contains a typo for `MANDATODY_LABEL`, so the documented SACL `MANDATORY_LABEL` spelling may not parse. The owner/group path reads `num_aces` with `le16toh` even though other code treats it as 32-bit, which is a signal to test against real descriptors.

## Test signals
Useful tests include raw SID parsing, name-to-SID plugin fallback, DACL add/delete/modify/set, `-A` canonical ordering, SACL `-U` operations, owner/group replacement with different SID lengths, empty DACL handling, large descriptor buffer growth, Azure-style descriptor offsets, invalid ACE forms, and verifying resulting ACLs with `getcifsacl` or `smbinfo secdesc` on a CIFS mount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/setcifsacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/setcifsacl.rst.in -->
# sources/user-network-fs/cifs-utils/setcifsacl.rst.in

## Purpose
This reStructuredText input is the manual page for `setcifsacl(1)`. It documents the command-line contract for modifying CIFS/NTFS security descriptor ACLs, SACLs, owner SIDs, and group SIDs on CIFS-mounted file objects.

## Important APIs and options
The documented interface exposes `-h`, `-v`, `-U`, `-a`, `-A`, `-D`, `-M`, `-S`, `-o`, and `-g`. ACE entries are documented as `ACL:SID:TYPE/FLAGS/MASK`, with multiple entries comma-separated inside quotes. DACL types include `ALLOWED`, `DENIED`, `OBJECT_ALLOWED`, and `OBJECT_DENIED`; SACL types include audit/object/callback/resource labels. Masks support symbolic `FULL`, `CHANGE`, `READ`, combinations of `R W X D P O`, or numeric hex values. Owner/group SIDs may be names or raw SID strings, relying on the configured idmap plugin.

## Control flow described
The manual describes one-shot transformations: add, add with preferred ordering, delete exact ACEs, modify ACEs matched by SID and type, replace an ACL, set owner SID, or set group SID. `-U` retargets ACE operations from DACL to SACL and is not meaningful for owner/group changes.

## State and persistence behavior
The documented state is the CIFS server-side security descriptor obtained and written through the Linux CIFS client. The manpage makes clear that server behavior decides whether the descriptor is actually applied and that kernel support is required.

## Dependencies and integration points
The template contains `@pluginpath@`, so build configuration injects the idmap plugin location. It cross-references `mount.cifs(8)` and `getcifsacl(1)` and should stay synchronized with `setcifsacl.c` parser behavior and cifs-utils install paths.

## Risks
There are documentation-code mismatches: the manpage uses `OBJECT_ALLOWED`/`OBJECT_DENIED`, while the C parser accepts `ALLOWED_OBJECT`/`DENIED_OBJECT`; DACL flag text mentions `NI`/`IA`, while code accepts `NP`/`I`; and SACL `MANDATORY_LABEL` is documented but the C parser contains a misspelled string. These mismatches can produce user-facing failures even when implementation logic works.

## Test signals
Run generated manpage builds, check examples against the compiled binary parser, and include documentation linting for option spellings and macro substitution. Integration tests should verify each example either succeeds or is intentionally corrected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/setcifsacl.rst.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/smb2-quota -->
# sources/user-network-fs/cifs-utils/smb2-quota

## Purpose
`smb2-quota` is a Python 3 command-line tool that queries quota information for a file on a Linux CIFS/SMB mount using the CIFS query-info ioctl.

## Important APIs, types, and functions
The script uses `fcntl.ioctl` with `CIFS_QUERY_INFO = 0xc018cf07`, an `array.array('B')` buffer, and `struct.pack_into`/`unpack_from` to marshal the quota request and response. `SID` decodes Windows SIDs. `QuotaEntry` decodes one quota record, formats used/threshold/limit fields, computes percentage and status, and prints tabular, CSV, or list output. `Quota` walks the variable-length quota entry chain through each entry's next-offset field. `parser_check` builds and submits the ioctl request.

## Control flow
`main` parses `--tabular`, `--csv`, `--list`, and a required filename. Tabular is the default when no format is chosen. Each selected format calls `parser_check`, which opens the file read-only, initializes a 16 KiB query buffer with quota info type and lengths, performs the ioctl, slices the returned payload, constructs `Quota`, and prints it.

## State and persistence behavior
The tool is read-only. It does not cache or persist data locally; all state comes from the mounted share via the kernel CIFS client and server quota support.

## Dependencies and integration points
It depends on Python 3 stdlib modules and Linux CIFS ioctl ABI support. It integrates with cifs.ko and a mounted SMB share path. Output is intended for humans or scripts, with CSV mode providing a stable simple form.

## Risks
The parser assumes a fixed 16 KiB buffer and does not retry on larger quota responses. `percent_used` divides by `limit` unless limit equals threshold; unlimited quota values can produce misleading percentages. It catches ioctl errors but does not exit nonzero explicitly. The request setup packs two adjacent one-byte fields both commented as "return single"; that warrants checking against the kernel ABI.

## Test signals
Unit-test SID decoding and chained quota parsing with synthetic buffers. On an SMB server with quotas enabled, test all output modes, unlimited and no-warning values, multiple entries, ioctl failures on non-CIFS files, and behavior when response size approaches the fixed buffer limit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/smb2-quota -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/smb2-secdesc -->
# sources/user-network-fs/cifs-utils/smb2-secdesc

## Purpose
`smb2-secdesc` is a Tk GUI helper for displaying the owner, group, DACL entries, and basic/advanced permission bits from a CIFS file security descriptor.

## Important APIs, types, and functions
The script uses `CIFS_QUERY_INFO = 0xc018cf07`, opens a target file, requests security info with owner/group/DACL bits, and decodes binary structures with `struct`. `SID`, `ACE`, `ACL`, and `SecurityDescriptor` model MS-DTYP structures. `App` builds a Tkinter UI with owner/group labels, an ACE list, and disabled checkbuttons for basic and advanced permission interpretation.

## Control flow
`main` requires a single filename, allocates a 16 KiB buffer, packs `InfoType: Security`, `AddInfo: Group/Owner/Dacl`, and input length, runs the ioctl, decodes the returned security descriptor, then starts a Tk event loop. Selecting ACEs updates the displayed permission checkbuttons.

## State and persistence behavior
The tool is read-only. It stores decoded descriptor data only in memory and does not modify server ACLs or local files.

## Dependencies and integration points
It depends on Linux CIFS ioctl support, Python GUI bindings, and a display environment. It overlaps functionally with `smbinfo secdesc` and `getcifsacl`, but presents a GUI view instead of text output.

## Risks
The file is Python 2 style despite a modern tree containing Python 3 utilities: it imports `Tkinter` and uses `print` statements without parentheses. On current Python 3 systems it will fail unless converted. There is little bounds checking for malformed descriptors. The UI maps only ACE types 0 and 1 for most views and ignores editing. One advanced checkbox appears wrong: `CHAN_PERM` updates `bf_adv_rp` instead of the change-permissions checkbox. The listbox width calculation uses `if max > len(sid)` rather than the likely intended less-than comparison.

## Test signals
Run syntax checks under the intended Python version, GUI smoke tests with Xvfb, descriptor decoding tests with synthetic owner/group/DACL buffers, and live ioctl tests on files and directories. Compare displayed flags against `smbinfo secdesc` for the same object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/smb2-secdesc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/smbinfo -->
# sources/user-network-fs/cifs-utils/smbinfo

## Purpose
`smbinfo` is a Python 3 command-line multiplexer for querying SMB-specific file, filesystem, snapshot, quota, security descriptor, compression, key, and tcon/session information through Linux CIFS ioctls.

## Important APIs, types, and functions
The script defines ioctl constants for `CIFS_QUERY_INFO`, `CIFS_ENUMERATE_SNAPSHOTS`, `CIFS_DUMP_KEY`, `CIFS_DUMP_FULL_KEY`, and `CIFS_GET_TCON_INFO`. `QueryInfoStruct` centralizes packing the query-info header and input/output buffer. Formatting helpers include `flags_to_str`, `type_to_str`, `win_to_datetime`, `guid_to_str`, and `bytes_to_hex`. Domain parsers include `SnapshotArrayStruct`, `SID`, `ACE`, `KeyDebugInfoStruct`, `FullKeyDebugInfoStruct`, and `SmbMntTconInfoStruct`. Subcommands cover file access/alignment/all/basic/EA/fs-size/internal/mode/position/standard/stream info, FSCTL object ID, compression get/set, snapshots, quota, secdesc, keys, and tcon info.

## Control flow
`main` builds an argparse subcommand table and dispatches to `cmd_*` handlers. Most handlers open the supplied file, instantiate a query struct with SMB info type/class/flags, call the ioctl, and hand the returned byte buffer to a `print_*` decoder. Snapshot listing uses a two-pass ioctl to discover and then fetch the array. Key dumping first tries the newer full-key ioctl and falls back to the older fixed-size key dump.

## State and persistence behavior
Most subcommands are read-only. `setcompression` changes remote file compression state through an FSCTL passthrough. `keys` exposes session material for network trace decryption and prints secrets to stdout.

## Dependencies and integration points
It depends on Python 3, Linux-specific CIFS ioctls, cifs.ko support for the requested info classes, and SMB server capabilities. It integrates with other cifs-utils ACL/quota tools by decoding the same SIDs, ACEs, quota records, and security descriptors.

## Risks
Manual binary parsing lacks response-length checks and can raise `struct.error` on short buffers. Some file descriptors are not closed on every path. `win_to_datetime` uses local timezone conversion, which may surprise users comparing SMB UTC values. `SID.subauth` stores one-element tuples due to missing `[0]`, so SID string formatting may be wrong for security descriptor output. `keys` can leak sensitive session keys and should remain privileged/debug oriented.

## Test signals
Add synthetic-buffer tests for each `print_*` parser, CLI parser tests for every subcommand, and live CIFS integration tests gated on a mounted share. Include negative tests on non-CIFS files, short ioctl responses, snapshot arrays, secdesc SID formatting, compression set/get, and key-dump permission failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/smbinfo -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/spnego.c -->
# sources/user-network-fs/cifs-utils/spnego.c

## Purpose
`spnego.c` builds ASN.1/SPNEGO and GSS-API wrapper blobs used by CIFS authentication helpers for Kerberos and SPNEGO negotiation.

## Important APIs, types, and functions
The file exports `spnego_gen_krb5_wrap` and `gen_negTokenInit`. Both return `DATA_BLOB` values and use the local ASN.1 helper API (`asn1_init`, `asn1_push_tag`, `asn1_write_OID`, `asn1_write`, `asn1_write_OctetString`, `asn1_pop_tag`, `asn1_free`) plus talloc memory contexts. OID constants come from `spnego.h`.

## Control flow
`spnego_gen_krb5_wrap` creates an ASN.1 application tag, writes the Kerberos 5 OID, appends a two-byte token id and the ticket bytes, then returns a copied blob. `gen_negTokenInit` builds an application SPNEGO wrapper containing a `negTokenInit` sequence with one mechanism OID and a mechanism token octet string.

## State and persistence behavior
The functions are pure encoders. They allocate temporary memory, copy the generated bytes into returned blobs, and persist no local or external state.

## Dependencies and integration points
This code integrates with CIFS upcall/authentication paths that need SPNEGO tokens. It depends on `data_blob.h`, `asn1.h`, `spnego.h`, and talloc. Consumers must free returned blobs according to the data blob contract.

## Risks
The disabled `data->has_error` checks mean ASN.1 build failures may still produce blobs unless underlying helpers encode errors into the returned data. `talloc_init` failure is not checked before `asn1_init`. Caller ownership and freeing of `DATA_BLOB` must be consistently documented.

## Test signals
Unit tests should compare generated DER bytes for known Kerberos wrap and negTokenInit fixtures, force ASN.1 allocation failures where possible, and validate interoperability with a Kerberos/SPNEGO acceptor.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/spnego.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/spnego.h -->
# sources/user-network-fs/cifs-utils/spnego.h

## Purpose
`spnego.h` declares SPNEGO/Kerberos OID constants, GSS token identifiers, and the encoder functions implemented by `spnego.c`.

## Important APIs and types
The header defines `OID_SPNEGO`, `OID_NTLMSSP`, `OID_KERBEROS5_OLD`, and `OID_KERBEROS5`. It also defines token-id byte strings for Kerberos AP-REQ/AP-REP/error and GSS MIC/wrap. It declares `gen_negTokenInit(const char *OID, DATA_BLOB blob)` and `spnego_gen_krb5_wrap(const DATA_BLOB ticket, const uint8_t tok_id[2])`.

## Control flow and state
The header has no runtime control flow or persistence. It is a compile-time contract for authentication token construction.

## Dependencies and integration points
It assumes `DATA_BLOB` and `uint8_t` are visible to includers before or through local include ordering. It is consumed by SPNEGO encoders and authentication helpers in cifs-utils.

## Risks
The token-id macros cast string literals to mutable `unsigned char *`, which can trigger const-correctness warnings and unsafe mutation if callers write through them. The header itself does not include `stdint.h` or `data_blob.h`, so standalone inclusion can fail depending on include order.

## Test signals
Compile tests should include this header directly in isolation and with strict warnings. API tests should verify token-id values and OID strings against expected SPNEGO/Kerberos constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/spnego.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/util.c -->
# sources/user-network-fs/cifs-utils/util.c

## Purpose
`util.c` provides small portability helpers for cifs-utils code paths that do not link Samba's libreplace: fallback `strlcpy`, fallback `strlcat`, and UID-to-username lookup.

## Important APIs and functions
When configure does not provide `HAVE_STRLCPY` or `HAVE_STRLCAT`, this file defines compatible `strlcpy` and `strlcat`. `getusername(uid_t uid)` wraps `getpwuid` and returns the passwd entry's `pw_name` pointer or `NULL`.

## Control flow
The string functions compute source/destination lengths, copy only what fits, always NUL-terminate when buffer size permits, and return the length that would have resulted. `getusername` performs a single passwd database lookup.

## State and persistence behavior
No persistent state is written. `getusername` returns a pointer owned by libc's passwd storage, which may be overwritten by later passwd calls.

## Dependencies and integration points
It depends on `<string.h>`, `<pwd.h>`, and `<sys/types.h>`, and exposes declarations through `util.h`. It is a portability layer shared by cifs-utils programs.

## Risks
`strlcpy` uses `if (bufsize <= 0)` even though `bufsize` is `size_t`; harmless but stylistically misleading. `getusername` comments "caller frees username if necessary", but the returned `pw_name` must not be freed, which can mislead callers. These replacements should match platform semantics exactly to avoid truncation bugs.

## Test signals
Unit-test truncation, zero-size buffers, exact-fit buffers, empty strings, overlapping assumptions, and return lengths against known `strlcpy`/`strlcat` behavior. Test `getusername` for existing and nonexistent UIDs without freeing the returned pointer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/util.h -->
# sources/user-network-fs/cifs-utils/util.h

## Purpose
`util.h` declares the cifs-utils portability helpers implemented in `util.c`.

## Important APIs
The public functions are `strlcpy`, `strlcat`, and `getusername`. The first two may map either to local replacements or platform functions depending on configure results; `getusername` maps a UID to a passwd username.

## Control flow and state
The header has no runtime flow or persistence. It forms an include contract for utility consumers.

## Dependencies and integration points
The declarations use `size_t` and `uid_t` but the header does not include `<stddef.h>` or `<sys/types.h>`, relying on includers to provide those types. It is included by `util.c` after the needed system headers.

## Risks
Standalone inclusion can fail under strict compilation because required typedefs are not self-contained. Declaring `strlcpy`/`strlcat` unconditionally can conflict if a platform prototype with different visibility is already present, although configure guards implementation emission.

## Test signals
Add a compile-only test that includes `util.h` first in a translation unit. Build with strict warnings on platforms with and without native `strlcpy`/`strlcat`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/.github/workflows/makefile.yml -->
# sources/user-network-fs/davfs2/.github/workflows/makefile.yml

## Purpose
This GitHub Actions workflow is the davfs2 CI build definition for pushes and pull requests targeting `main`.

## Important APIs and jobs
It defines one `build` job on `ubuntu-latest`. Steps check out the repository with `actions/checkout@v4`, run `.github/workflows/setup-ubuntu.sh`, configure with `meson setup build`, compile with `ninja -C build`, and run `meson dist -C build --allow-dirty`.

## Control flow
The workflow is linear: dependency installation, Meson configuration, Ninja build, and Meson distcheck. Any failing command fails the job.

## State and persistence behavior
No project state is persisted outside the transient GitHub runner workspace. Dependency state comes from the runner apt environment.

## Dependencies and integration points
It integrates with GitHub Actions, Meson, Ninja, po4a, libneon development headers, and the repository's Meson build files. Dist generation also validates install/dist metadata.

## Risks
`ubuntu-latest` can change underneath the project, altering compiler, Meson, and libneon versions. There is no dependency cache, matrix, sanitizer, or test step beyond build/dist. The workflow name says "Makefile CI" even though it uses Meson/Ninja.

## Test signals
CI success should prove Meson configure/build and dist packaging. Improvements should test multiple Ubuntu versions or compiler modes, and include a minimal runtime or unit test target if available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/.github/workflows/makefile.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/.github/workflows/setup-ubuntu.sh -->
# sources/user-network-fs/davfs2/.github/workflows/setup-ubuntu.sh

## Purpose
This shell script installs the Ubuntu packages needed by davfs2's CI workflow.

## Important APIs and commands
It runs with `/bin/sh`, enables `set -ex`, defines `PACKAGES` as `libneon27-dev`, `meson`, `ninja-build`, and `po4a`, then invokes `sudo -E apt-get -y install $PACKAGES`.

## Control flow
The script is a single install step. `set -e` stops on errors and `set -x` logs commands for CI diagnosis.

## State and persistence behavior
It mutates only the ephemeral CI runner by installing apt packages. No repository files are changed.

## Dependencies and integration points
It assumes an Ubuntu GitHub runner with apt metadata already suitable for package install. It supports `.github/workflows/makefile.yml`.

## Risks
No `apt-get update` is run, so stale runner package indexes can break installs. Package names are Ubuntu-specific. `sudo -E` preserves environment variables, which is normal in CI but should be intentional.

## Test signals
The workflow build is the main signal. A shellcheck pass and periodic CI run on a fresh runner image can catch package rename or apt metadata issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/.github/workflows/setup-ubuntu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/etc/davfs2.conf -->
# sources/user-network-fs/davfs2/etc/davfs2.conf

## Purpose
This is the installed template/default configuration file for davfs2. It lists supported options and default values, almost entirely commented out, for administrators and users to enable as needed.

## Important options
It groups options into general daemon settings (`dav_user`, `dav_group`, `buf_size`), WebDAV behavior (`use_proxy`, certificates, secrets, auth prompts, locks, ETags, cookies, redirects, timeouts, retries, headers), cache behavior (`backup_dir`, `cache_dir`, `cache_size`, refresh intervals, upload delay, GUI optimization, memory minimization, lookup sync), and debug categories.

## Control flow
There is no executable flow. The runtime parser in davfs2 consumes uncommented keyword/value lines from system and user config files, with mount-specific sections documented elsewhere.

## State and persistence behavior
When installed, this file becomes part of persistent system configuration under the davfs2 sysconf directory. Most lines are comments and therefore do not override compiled defaults until edited.

## Dependencies and integration points
It is installed by `etc/meson.build` and should stay aligned with `man/davfs2.conf.5.in` and the runtime option parser. It references cache directories, secrets files, cert directories, and syslog debug behavior.

## Risks
Default drift is visible: this template says `buf_size 64`, while the manpage states default 16. It also lists `sync_on_lookup`, which is not covered in the read English manpage. Documentation/config drift can make administrator expectations wrong. Debug options can expose secrets if enabled.

## Test signals
Package installation tests should verify the file lands in the expected sysconf directory. Parser tests should load representative uncommented options and mount-specific sections. Documentation checks should compare option names/defaults between this template, manpage, and parser tables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/etc/davfs2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/etc/meson.build -->
# sources/user-network-fs/davfs2/etc/meson.build

## Purpose
This Meson build fragment installs davfs2 system configuration templates, secrets placeholders, certificate directories, and shared template copies.

## Important APIs and targets
It calls `install_data` for `secrets` with `install_mode : 'rw-------'`, installs `davfs2.conf` into `davfs2_sysconfdir`, installs certificate directories using either `install_emptydir` for Meson >= 0.60.0 or `install_subdir` fallback for older Meson, and installs `davfs2.conf` plus `secrets` into `davfs2_sharedir`.

## Control flow
The only branch is the Meson version check. Newer Meson creates empty directories directly; older Meson copies checked-in directory placeholders.

## State and persistence behavior
At install time it creates or copies persistent configuration and certificate storage locations. The secrets file mode is security-sensitive.

## Dependencies and integration points
It depends on top-level Meson variables such as `davfs2_sysconfdir`, `davfs2_certdir`, and `davfs2_sharedir`. It connects source templates under `etc/` to runtime lookup paths documented in the manpages.

## Risks
Fallback `install_subdir('private', install_dir : davfs2_sysconfdir / davfs2_certdir)` relies on source directory shape and may copy contents rather than only creating empty directories. Directory permissions for cert/private directories are not explicitly set in the new `install_emptydir` path. Any mismatch with runtime expectations can break certificate or secret lookup.

## Test signals
Run `meson install --destdir` and assert installed file paths and modes, especially `secrets` mode and certificate/private directory existence. Test both Meson version paths if compatibility is still intended.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/etc/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/davfs2.conf.5.in -->
# sources/user-network-fs/davfs2/man/davfs2.conf.5.in

## Purpose
This template generates the `davfs2.conf(5)` manpage. It documents system/user configuration precedence, mount-specific sections, syntax and quoting rules, and all major davfs2 configuration options.

## Important APIs and options
The file uses roff man macros with Meson/config placeholders such as `@CONFIGFILE@`, `@PROGRAM_NAME@`, `@SYS_CONF_DIR@`, `@PACKAGE@`, and directory defaults. It documents general options, WebDAV/TLS/auth/lock behavior, cache settings, and debug categories. Notable operational options include certificate trust controls, `secrets`, `ask_auth`, `use_locks`, ETag workarounds, redirects, timeouts, retry limits, `max_upload_attempts`, `add_header`, cache sizing, refresh windows, delayed upload, GUI optimization, and memory minimization.

## Control flow described
The manpage specifies parser semantics: root reads only the system config, ordinary users also read the user config with user settings taking precedence, global options precede mount-specific bracketed sections, and section options override globals for that mount.

## State and persistence behavior
It documents persistent config files, secrets paths, cache directories, cert lookup directories, syslog debug output, lock behavior, local cache lifetime, and backup handling for failed uploads.

## Dependencies and integration points
The template is transformed by the build system and installed as section 5 documentation. It must stay aligned with the shipped `etc/davfs2.conf`, mount helper parser, German PO translations, and `mount.davfs(8)` documentation.

## Risks
The manpage has several spelling issues in source text (`brakets`, `otion`, `thes`, `propably`) and may not include every option from `etc/davfs2.conf` (`sync_on_lookup` appears in config but not here). Security-sensitive options such as `trust_server_cert`, `debug secrets`, `add_header`, and `follow_redirect` require accurate warnings because they affect TLS validation, log exposure, and credential reuse.

## Test signals
Build the generated manpage, run manpage linting, verify placeholder substitution, and compare option names/defaults against parser tables and `etc/davfs2.conf`. Translation update tests should regenerate PO references from this source.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/davfs2.conf.5.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/de/davfs2.conf.5.po.in -->
# sources/user-network-fs/davfs2/man/de/davfs2.conf.5.po.in

## Purpose
This PO input provides the German translation for the generated `davfs2.conf(5)` manpage.

## Important APIs and structure
It is gettext/po4a data with metadata headers, source references, message flags, `msgid` English source text, and `msgstr` German translations. Placeholders such as `@CONFIGFILE@`, `@PROGRAM_NAME@`, `@SYS_CONF_DIR@`, `@PACKAGE@`, and roff formatting markers must be preserved exactly. It covers syntax rules, precedence, all documented config option names/defaults, debug categories, authors, home, and see-also sections.

## Control flow
There is no runtime flow. During documentation build, po4a/gettext tooling combines this translation with generated source manpage content to produce a localized section 5 page.

## State and persistence behavior
The output is installed documentation only. It does not alter runtime config state, but incorrect translation can cause persistent misconfiguration by administrators.

## Dependencies and integration points
It is installed through `man/de/meson.build` and depends on po4a-compatible syntax. It must track `man/davfs2.conf.5.in` and generated message references.

## Risks
Header metadata is stale relative to the 2026 POT creation date: project version and revision date are older. The source includes translated warnings for security-sensitive certificate, secrets, ETag, cache, and debug behavior, so stale or inaccurate text has operational risk. Some translated text includes typos, but no fuzzy markers were found in the inspected option list.

## Test signals
Run po4a/msgfmt validation, build the German manpage, check placeholder preservation, and compare message coverage against the current POT. Review translations for changed options and security warnings after any English source update.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/de/davfs2.conf.5.po.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/de/meson.build -->
# sources/user-network-fs/davfs2/man/de/meson.build

## Purpose
This Meson fragment configures installation of German localized davfs2 manpages.

## Important APIs and targets
It uses `configure_file` three times: `davfs2.conf.5.in.po` to `davfs2.conf.5` under `man5`, `mount.davfs.8.in.po` to `mount.davfs.8` under `man8`, and `umount.davfs.8.in.po` to `umount.davfs.8` under `man8`, all with the `mandata` configuration object.

## Control flow
The file has no conditionals. Meson substitutes configured variables into each localized PO-derived manpage input and installs the outputs.

## State and persistence behavior
At install time it writes localized documentation into `${mandir}/de`. It does not affect runtime behavior.

## Dependencies and integration points
It depends on top-level `mandata` and `mandir` definitions and on the German translation input filenames matching the build tree. It integrates the localization files into packaging/install output.

## Risks
The input names in this Meson file include `.in.po`, while the researched files are named `.po.in`; if the repository does not generate or rename those intermediates elsewhere, this can break localized manpage installation. There is no validation in this fragment that translated messages are complete.

## Test signals
Run `meson setup` and `meson install --destdir`, verify German manpages are generated and installed, and inspect build logs for missing input files. Add an install test that checks all three outputs exist under the expected language directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/de/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/de/mount.davfs.8.po.in -->
# sources/user-network-fs/davfs2/man/de/mount.davfs.8.po.in

## Purpose
This PO input provides the German translation for the `mount.davfs(8)` manpage, covering WebDAV mounting behavior, options, security policy, caching, locks, files, environment variables, examples, bugs, and references.

## Important APIs and structure
It is gettext/po4a data with roff references and Meson placeholders. It documents translated command forms, mount options such as `conf`, `dir_mode`, `file_mode`, `uid`, `gid`, `user`, `users`, `_netdev`, `username`, environment variables such as `DAVFS_PASSWORD`, proxy variables and `no_proxy`, plus file paths for config, secrets, certs, runtime PID files, and caches.

## Control flow described
The translated page describes how `mount` invokes the helper, how options are interpreted, how privileges drop to davfs2 user/group, how ordinary-user mounting is constrained by group membership and fstab, how cache state is reused, and how lock/lost-update recovery works.

## State and persistence behavior
It documents persistent cache directories, secrets files, certificate stores, PID files, fstab entries, and local-only permission metadata. It also documents that unmounting stores cached attributes and that local backup files can appear under `lost+found`.

## Dependencies and integration points
It is built and installed through the German manpage Meson path and must track the English `mount.davfs.8` source. Its environment variable and 2FA text must remain synchronized with the implementation, especially for scripted mounts.

## Risks
The inspected file contains untranslated `msgstr ""` entries for `DAVFS_PASSWORD` and its explanatory paragraph, and a fuzzy translation for the 2FA example that still uses the older credential example text. That means German documentation can omit or misstate newer authentication behavior. Since these entries affect password handling and CI mounting, they are higher-risk translation gaps.

## Test signals
Run po4a/msgfmt validation with fuzzy/untranslated checks, build the German manpage, and inspect rendered ENVIRONMENT and EXAMPLES sections. Add a release check that rejects fuzzy entries for security/authentication-related messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/de/mount.davfs.8.po.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/de/umount.davfs.8.po.in -->
# sources/user-network-fs/davfs2/man/de/umount.davfs.8.po.in

## Purpose
This PO input provides the German translation for `umount.davfs(8)`, the unmount helper manual.

## Important APIs and structure
It preserves placeholders such as `u@PROGRAM_NAME@`, `@PACKAGE@`, `@SYS_RUN@`, and references shared section translations from other davfs2 manpages. It documents `u@PROGRAM_NAME@`, `umount dir`, version/help options, ignored compatibility options `-f -l -n -r -v -t`, PID-file lookup under `@SYS_RUN@`, and see-also references.

## Control flow described
The manual explains that the helper is called by `umount(8)` and waits until `mount.davfs` has synchronized cached files to the WebDAV server. It advises `umount -i` if the daemon has serious errors and the helper cannot complete.

## State and persistence behavior
The documented state is cached dirty data pending upload and PID files for running davfs processes. Correct unmount behavior affects whether local cache changes have been synchronized before command return.

## Dependencies and integration points
It is installed through German manpage build rules and must align with the `u@PROGRAM_NAME@` helper, `umount(8)` behavior, runtime PID directory, and mount documentation.

## Risks
The header copyright line contains `2914`, likely a typo for 2014. The PO revision is much older than the POT creation date, so source drift should be reviewed even though this file is much smaller than mount/config translations. Misdocumentation here can lead users to bypass synchronization with `umount -i` without understanding data-loss implications.

## Test signals
Run msgfmt/po4a validation, build the rendered manpage, check placeholders, and verify option text against the actual unmount helper parser. Include translation freshness checks when English unmount documentation changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/de/umount.davfs.8.po.in -->
