# subset-b-007826 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-genconfig -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-genconfig

Purpose: `pvfs2-genconfig` is the Perl configuration generator for a new OrangeFS/PVFS2 file system. It can run interactively through `Term::ReadLine`, non-interactively through `Getopt::Long`, or write to stdout with `-`. Its output is an OrangeFS configuration file containing defaults, aliases, file-system handle ranges, storage hints, optional server-specific options, and optional key-, certificate-, LDAP-, or trusted-network security sections.

Important APIs, types, and functions: the script depends on `Term::ReadLine`, `Getopt::Long`, `Math::BigInt`, and `FindBin`. Most behavior is held in global option variables and `%all_endpoints`, whose entries carry `ALIAS`, `TYPE`, `HOSTNAME`, `PORTMAP`, `STORAGE`, `METASTORAGE`, and `LOGFILE`. Endpoint type flags are `$META_ENDPOINT` and `$IO_ENDPOINT`. Key routines include `parse_hostlist`, `get_specs`, `get_protocol`, protocol port helpers, `get_ionames`, `get_metanames`, `get_aliases`, `get_bmi_endpoint`, `emit_defaults`, `emit_aliases`, `emit_filesystem`, `emit_serveropts`, `emit_security`, `emit_distribution`, and `emit_fs_key`.

Control flow: startup discovers an installation root from `FindBin`, parses options, opens either the target config path or stdout, validates quiet/spec/security combinations, and establishes an output stream. Non-quiet mode creates a readline terminal and prompts for missing values. The generator then either parses explicit `--iospec`/`--metaspec` endpoint specifications or prompts/uses enumerated server names plus shared protocol and storage defaults. Missing endpoint storage/log fields are filled from defaults. It calculates endpoint counts, optionally prompts for security data, validates the server list, derives filesystem defaults, and emits `<Defaults>`, `<Aliases>`, `<FileSystem>`, and per-server `<ServerOptions>` when metaspec mode is used. `emit_filesystem` divides the configured handle span with `Math::BigInt`, reserves future ranges, sets distributed-directory controls, storage hints, optional generated `SecretKey`, and data distribution parameters.

State and persistence: the primary persistent artifact is the generated fs config file. If `--genkey` is enabled, `emit_fs_key` shells out to `openssl rand -base64 20` and embeds a newly generated secret key in the config. No source tree state is updated, but the script reads sentinel files `.pvfs2-genconfig-key` and `.pvfs2-genconfig-cert` beside the script to force security prompts. Generated file size is checked against `PVFS_REQ_LIMIT_CONFIG_FILE_BYTES` guidance, warning if it exceeds 65536 bytes.

Dependencies and integration points: generated config syntax targets OrangeFS server/client config parsers. Network endpoint output uses BMI module names such as `bmi_tcp`, `bmi_gm`, `bmi_mx`, `bmi_ib`, `bmi_rdma`, and `bmi_portals`. Security output integrates with OrangeFS server key/keystore/CA/user certificate and LDAP mapping directives. The default install root, storage, metadata, log, and security paths assume `/opt/orangefs` unless overridden.

Risks: the file uses many globals, so option interactions are easy to regress. There are apparent correctness hazards: `$fs_path` is referenced as bare `fs_path` in the defaulting check under `strict vars`; `parse_hostlist` appears not to push single values from brace lists; `get_ionames` and `get_metanames` are called with fewer arguments than their signatures expect in the non-spec path; distributed-directory emission contains stray debug `print "1\n"`, `print "2\n"`, and `print "3\n"` calls; `lt`/`gt` string comparisons are used for numeric distributed-directory bounds; and several regex parsers accept partially malformed endpoint specs. Security-sensitive values such as LDAP bind password can be written directly into config output.

Test signals: useful tests include `perl -c pvfs2-genconfig`, quiet-mode config generation for host-list and `--iospec`/`--metaspec` modes, brace host expansion with singletons and ranges, multi-protocol endpoint parsing, security-key and security-cert config generation including `_ALIAS_` substitution, default-output size warning behavior, and negative tests for missing quiet inputs, invalid protocols, missing keystore/server key pairs, bad distributed-directory limits, and absent `openssl` when `--genkey` is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-genconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-gencred.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-gencred.c

Purpose: `pvfs2-gencred.c` emits an encoded `PVFS_credential` object in binary form to stdout for callers that need OrangeFS credentials. It signs credentials with a private key when possible and deliberately falls back to unsigned credentials for operations that do not require permissions, such as `statfs`.

Important APIs, types, and functions: local `options_t` carries `user`, `group`, `timeout`, `keypath`, and optional `certpath`. The code uses `PVFS_credential`, `PVFS_uid`, `PVFS_gid`, `PVFS_REQ_LIMIT_GROUPS`, `PVFS_REQ_LIMIT_ISSUER`, `PVFS2_DEFAULT_CREDENTIAL_TIMEOUT`, and `PVFS2_DEFAULT_CREDENTIAL_KEYPATH`. Major functions are `is_idnum`, `parse_options`, `create_credential`, optional `get_certificate_keypath`, `sign_credential`, `write_credential`, `safe_write`, and `allowed`. OpenSSL APIs include `PEM_read_PrivateKey`, `EVP_SignInit_ex`, `EVP_SignUpdate`, `EVP_SignFinal`, `PEM_read_X509`, `i2d_X509_bio`, and error cleanup calls. Serialization is via `encode_PVFS_credential` from `pvfs2-req-proto.h`.

Control flow: `main` initializes OpenSSL, parses options, resolves requested numeric uid/gid or defaults to the current process, validates ids against `PVFS_UID_MAX`, and checks authorization with `allowed`. It obtains supplemental groups with `getgrouplist` when available and normalizes the primary group to the first slot. If user lookup or group lookup fails, it falls back to a single primary group but may still sign. `create_credential` populates issuer, uid, groups, and optional certificate data. If creation succeeds and signing is allowed, `sign_credential` opens the private key, warns on world permissions, signs the credential fields plus timeout, and stores the signature. Finally `write_credential` rejects tty stdout, encodes the fixed-size credential buffer, and writes it with EINTR-aware `safe_write`.

State and persistence: the tool does not persist files directly; it writes one binary credential record to stdout. It reads passwd/group databases, optional certificate and key files, and the service user authorization file from `PVFS2_SERVICEFILE` or `PVFS2_DEFAULT_CREDENTIAL_SERVICE_USERS`. In certificate mode it embeds DER certificate bytes in the credential and uses `$HOME/.pvfs2-cert.pem` and `$HOME/.pvfs2-cert-key.pem` defaults when paths are omitted.

Dependencies and integration points: this is tightly coupled to OrangeFS request protocol encoding and credential verification on servers. It relies on system identity APIs (`getuid`, `getgid`, `getpwuid`, `getpwnam_r`, `getgrouplist`), OpenSSL, and generated protocol encode functions. It is likely invoked by utilities or client wrappers that expect a binary credential on stdout rather than human-readable output.

Risks: unsigned fallback is intentional but security-sensitive, so callers must not treat every successful write as an authorization-capable credential. The service user parsing path allocates `service_data_buf` only after an `ERANGE` retry, yet passes it to `getpwnam_r` initially as NULL with a nonzero size, which is not portable. `strncat(def_certpath, def_certfile, sizeof(def_certfile))` depends on prior length checks but uses the source length rather than remaining buffer size. SHA-1 signing is legacy. Some fatal and warning paths continue into unsigned output, which is correct by design but easy to misinterpret in automation.

Test signals: run with stdout redirected to a file or pipe and verify tty stdout is rejected. Cover current-user credentials, explicit numeric `-u`/`-g`, invalid nonnumeric ids, invalid and valid `-t`, missing key files, insecure key permissions, service-user authorization allow/deny, certificate-enabled builds with missing and valid cert/key files, and binary decoding round trips against `decode_PVFS_credential` or server-side credential validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-gencred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-get-uid.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-get-uid.c

Purpose: `pvfs2-get-uid.c` queries OrangeFS management servers for UID activity statistics and prints per-server UID counters and time ranges. It can target explicit BMI server addresses or discover all servers for a filesystem.

Important APIs, types, and functions: `struct options` holds history seconds, a fixed-size `server_list`, `server_count`, and optional `PVFS_fs_id`. The code uses `PVFS_util_init_defaults`, `PVFS_util_gen_credential_defaults`, `PVFS_util_get_default_fsid`, `BMI_addr_lookup`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, `PVFS_mgmt_get_uid_list`, `PINT_util_get_current_timeval`, and `PINT_util_parse_timeval`. Returned records are `PVFS_uid_info_s` arrays sized by `UID_MGMT_MAX_HISTORY`.

Control flow: after parsing `-s`, `-t`, `-f`, and `-h`, the program defaults missing history to `UID_HISTORY_MAX_SECS`. It initializes OrangeFS defaults and credentials, selects the filesystem id, builds a BMI address array either from repeated `-s` options or by querying all servers, allocates one UID history buffer per server plus count buffers, then calls `PVFS_mgmt_get_uid_list`. The output includes fsid, current time, server URI, and each UID record's uid, count, start timestamp, and last timestamp. `cleanup` frees options, server strings, address arrays, and per-server stats arrays.

State and persistence: no persistent state is written. The tool reads OrangeFS configuration through the util initialization path and samples server-side UID history. Its only durable effect is stdout/stderr output.

Dependencies and integration points: it integrates with BMI for address lookup and with the management API's UID tracking feature. If server addresses are not supplied, it depends on cached config and management server enumeration to map the filesystem to servers. Time formatting comes from internal `PINT_util_*` helpers.

Risks: `server_list` is allocated for `UID_SERV_LIST_SIZE`, but in auto-discovery mode the code stores discovered server strings into `prog_opts->server_list[i]` for `server_count` without capping `server_count` to 64. Several error paths return without `PVFS_sys_finalize` or cleanup. `uid_info_count` allocation failure logs an error but does not immediately return before later use. `atoi` parsing gives weak validation for history and fsid. The server-limit branch checks equality then greater-than in a way that still leaves parsing behavior somewhat unclear.

Test signals: exercise explicit single and repeated `-s` lookups, auto-discovery, invalid BMI address, default fsid lookup, explicit `-f`, invalid negative `-f`, `-t 0`, large server counts above 64, management API failures, and output formatting for empty and populated UID history arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-get-uid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-get-user-cert.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-get-user-cert.c

Purpose: `pvfs2-get-user-cert.c` enrolls a user for certificate-based OrangeFS security. It prompts for a filesystem username and password, requests a certificate and private key from OrangeFS management servers, and stores them in user-selected or default paths.

Important APIs, types, and functions: `struct options` carries `fs_userid`, expiration days, key path, cert path, and a Windows system-user flag. Key functions are `sec_error`, `get_default_path`, `get_file_paths`, `get_current_userid`, `store_cert_and_key`, `get_option_value`, `parse_args`, and Windows-only `get_module_dir`, `open_config_file`, and `get_tab_file`. OrangeFS APIs include `PVFS_util_parse_pvfstab`, `PVFS_sys_initialize`, `PVFS_sys_fs_add`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, and `PVFS_mgmt_get_user_cert`. Certificate helpers include `PINT_cert_to_X509`, `PINT_save_cert_to_file`, `PINT_save_privkey_to_file`, `PINT_cleanup_cert`, `PINT_cleanup_key`, and `PINT_get_security_path`.

Control flow: `main` parses options, initializes OpenSSL, determines the filesystem userid from an argument, current local user, or prompt, then reads the password with `EVP_read_pw_string`. It parses `pvfstab` or Windows tabfile, initializes sysint, prompts for filesystem selection if multiple entries exist on non-Windows, adds the selected filesystem, collects all server addresses, and calls `PVFS_mgmt_get_user_cert`. On success, `store_cert_and_key` resolves output paths, converts the returned certificate buffer to X509, writes the certificate, decodes the DER RSA private key into an EVP key, writes the private key, and chmods both files to user read/write on non-Windows.

State and persistence: this utility persists sensitive credentials. On Unix defaults are `$HOME/.pvfs2-cert.pem` and `$HOME/.pvfs2-cert-key.pem`, with `PVFS2CERT_FILE` and `PVFS2KEY_FILE` overrides. On Windows paths may come from command options, `%USERNAME%`-substituted config entries, profile defaults, or the module directory for `--system`. It reads `pvfstab`/`orangefstab`, OrangeFS config, environment variables, and server certificate enrollment state.

Dependencies and integration points: it bridges local user interaction, OpenSSL conversion and storage, and OrangeFS management certificate issuance. The generated files are consumed by `pvfs2-gencred` and client credential generation in certificate-security mode. Windows support depends on `Windows.h`, `UserEnv.h`, and config discovery in the executable directory.

Risks: `get_default_path` is a TODO on non-Windows but returns success, although Unix flow currently builds defaults elsewhere. Several error exits before `exit_main` can skip `PVFS_sys_finalize`. `addr_array` is not initialized before all failure paths and is freed only on the success path after server array allocation. `scanf` usage for prompts has limited input handling and may leave buffered input surprises. The Windows config parser has a suspicious whitespace condition `(*pline != ' ' || *pline == '\t')`. The program handles private keys and passwords, so file permissions, path truncation, and logging must be treated as security-sensitive.

Test signals: test Unix default path creation, explicit `-k`/`-c`, environment overrides, invalid and valid `--expiration`, empty username prompt, multiple filesystem selection including quit, bad pvfstab, server enumeration failure, invalid password mapping to access errors, returned malformed cert/key buffers, chmod failures, and Windows config/path substitution behavior when building on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-get-user-cert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-getmattr -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-getmattr

Purpose: `pvfs2-getmattr` is a small Bash wrapper that retrieves OrangeFS mirroring attributes for a target file. It prints the mirror copy count, mirror mode, or both by delegating to `pvfs2-xattr`.

Important APIs, types, and functions: there are no custom data types. The script defines `usage`, parses `-c`, `-m`, and `-f`, checks for `pvfs2-xattr` with `which`, validates the target with `pvfs2-stat`, and reads xattrs with `pvfs2-xattr -k user.pvfs2.mirror.copies -t "$TARGET"` and `pvfs2-xattr -k user.pvfs2.mirror.mode -t "$TARGET"`.

Control flow: argument count must be between two and four. Flags set `COPY` and `MODE`; `-f` consumes the following target and requires `pvfs2-stat` to succeed. If neither `-c` nor `-m` is supplied, both are enabled. The script then conditionally invokes `pvfs2-xattr` once for each requested mirror attribute.

State and persistence: no state is written. It reads extended attributes from the target OrangeFS object and depends on the called tools for all filesystem access and authentication.

Dependencies and integration points: `pvfs2-getmattr` is part of the admin command suite and composes `pvfs2-stat` plus `pvfs2-xattr`. It assumes those commands are on `PATH`; despite the comment mentioning both commands, only `pvfs2-xattr` is explicitly checked with `which`.

Risks: `which pvfs2-xattr` only treats exit code `1` as missing and ignores other failures. `pvfs2-stat` is not checked for presence before use. `-f` without a following value calls `pvfs2-stat` with an empty argument and falls into usage. The script exits without explicit nonzero codes in several usage/error paths, relying on shell function behavior. There is no support for multiple files or for distinguishing absent xattrs from command failures.

Test signals: run with no args, too many args, `-f` missing value, nonexistent target, target lacking mirror xattrs, `-c`, `-m`, default both, missing `pvfs2-xattr`, missing `pvfs2-stat`, and targets with spaces to confirm quoting remains safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-getmattr -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-ln.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-ln.c

Purpose: `pvfs2-ln.c` implements symlink creation for OrangeFS paths. Hard links are explicitly unsupported; callers must pass `-s`.

Important APIs, types, and functions: `struct options` stores link target, link name, and verbosity. The main operations use `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PINT_remove_base_dir`, `PINT_lookup_parent`, and `PVFS_sys_symlink`. OrangeFS types include `PVFS_credential`, `PVFS_fs_id`, `PVFS_sys_attr`, `PVFS_object_ref`, and `PVFS_sysresp_symlink`.

Control flow: `parse_args` accepts `-s`, `-V`/`--verbose`, `-v`/`--version`, and help. It rejects calls without `-s` or without exactly `TARGET LINK_NAME`. `main` initializes sysint defaults, resolves the link name into filesystem id and PVFS-relative path, generates default credentials, and calls `make_link`. `make_link` builds symlink attributes from credential owner/group and mode `0777`, extracts the final link basename, rejects root creation, looks up the parent handle, and invokes `PVFS_sys_symlink` with the user-supplied target string.

State and persistence: the persistent effect is a new symlink object in the OrangeFS namespace. No local files are written. The target string is stored in the symlink object and is not resolved by this tool.

Dependencies and integration points: it follows the same admin utility sysint pattern as other tools in this directory and relies on internal helpers from `pint-sysint-utils.h` and `pvfs2-internal.h`. Credential generation uses the default environment/config-driven OrangeFS credential path.

Risks: error text after `PVFS_util_resolve` mentions `pszLinkTarget` even though resolving the link name failed. `PVFS_sys_finalize` is not called on all error paths. Attributes use all settable fields even though only owner, group, and perms are initialized; zeroed timestamps may be interpreted depending on sysint expectations. The code uses internal `PINT_*` helpers with TODO comments saying they should become public utility APIs. It does not implement POSIX `ln` option compatibility beyond `-s`.

Test signals: cover missing `-s`, hard-link rejection, bad argument count, link name outside pvfstab, missing parent directory, existing link name, successful symlink to absolute and relative targets, verbose output, version output, and permission-denied credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-ln.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-ls.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-ls.c

Purpose: `pvfs2-ls.c` is the OrangeFS-aware `ls` implementation. It lists files or directory contents from mounted OrangeFS filesystems, with long, recursive, inode, hidden-file, owner/group, human-readable size, and timing/verbose options.

Important APIs, types, and functions: `struct options` holds display flags and up to `MAX_NUM_PATHS` start paths. `print_entry_attr` formats permissions, type, owner/group, size, timestamps, symlink targets, and inode. `print_entry` decides whether to print short or long entries and can fetch attributes if not provided. `do_list` performs lookup, getattr, readdirplus iteration, recursive directory queuing, and directory-version checks. The tool uses `PVFS_util_parse_pvfstab`, `PVFS_sys_initialize`, `PVFS_sys_fs_add`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_sys_lookup`, `PVFS_sys_getattr`, `PVFS_sys_getparent`, `PVFS_sys_readdirplus`, and `PVFS_util_release_sys_attr`.

Control flow: main parses Unix or Windows variants of options, parses pvfstab, initializes all filesystems listed in the tab, defaults to the first mount directory when no path is supplied, resolves each requested path, trims the user-facing mount prefix to mimic `/bin/ls`, normalizes slashes, and calls `do_list`. `do_list` looks up the object without following symlinks, handles single files/symlinks or `--directory` directories directly, otherwise iterates directory entries using `PVFS_sys_readdirplus` in batches of `MAX_NUM_DIRENTS`. For recursive listing it builds a linked list of child directory paths and calls itself after completing the current directory.

State and persistence: the command is read-only against OrangeFS metadata. It allocates temporary buffers for entry formatting, readdirplus responses, and recursive path lists, and releases returned sysattrs after each batch. It reads system passwd/group databases for name display unless numeric output is requested.

Dependencies and integration points: it is a client of OrangeFS sysint and pvfstab mount configuration. Formatting utilities come from `str-utils.h` and internal helpers such as `PINT_string_rm_extra_slashes_rts`. It maps OrangeFS permission bits and object types to Unix-like display conventions.

Risks: recursive traversal does not skip `.`-prefixed directories when not listing hidden entries because recursion checks `attr->objtype` independently of whether `print_entry_attr` suppresses output. Symlink attrs require `link_target` when long output is used. There is duplicated cleanup for `rdplus_response` after the loop that is mostly harmless due to count/token state but fragile. Main mutates `user_opts->start[i]`, which points into argv for user-supplied paths. `--all-times` appears in the long option table, but the Unix parser label is unreachable from a long-option branch without a `case` value assignment pattern that relies on `goto`; this deserves direct option tests. Error paths may skip cleanup/finalize.

Test signals: compare output for files, symlinks, directories, root, multiple paths, `-l`, `-n`, `-g`, `-o`, `-G`, `-i`, `-a`, `-A`, `-d`, `-R`, `-h`, `--si`, `--all-times`, and `-t` timing. Include directory mutation during listing to exercise verbose version warnings, very long names near `ENTRY_MAX`, hidden recursive subdirectories, and mount-prefix trimming across non-root and root mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-ls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-mkdir.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-mkdir.c

Purpose: `pvfs2-mkdir.c` creates one or more OrangeFS directories, with options for mode, parent creation, and distributed-directory sizing hints.

Important APIs, types, and functions: `struct options` stores directory arguments, mode, `init_num_dirdata`, `max_num_dirdata`, `split_size`, verbosity, and parent creation. Key functions are `parse_args`, `make_directory`, `read_mode`, `read_init_num_dirdata`, `read_max_num_dirdata`, `read_split_size`, `enable_verbose`, and `enable_parents`. OrangeFS calls include `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_sys_lookup`, and `PVFS_sys_mkdir`. It uses `PVFS_sys_attr` fields `distr_dir_servers_initial`, `distr_dir_servers_max`, and `distr_dir_split_size`.

Control flow: parsing accepts up to `MAX_NUM_DIRECTORIES`, fills defaults for mode and dirdata controls, and stores argv directory pointers. Main allocates parallel arrays for PVFS-relative paths and fsids, initializes OrangeFS, resolves every requested directory, generates one credential, and calls `make_directory` for each. `make_directory` splits the target PVFS path into parent and basename with `dirname`/`basename`, rejects root, populates directory attributes, looks up the parent, optionally recurses to create missing parents on `-p`, then calls `PVFS_sys_mkdir`.

State and persistence: successful calls persist new directory objects in OrangeFS metadata, including permission bits and distributed-directory hints. No local files are written. The command reads the process umask through `PVFS_util_get_umask` when no mode is supplied.

Dependencies and integration points: it follows sysint admin utility conventions and relies on `libgen` path mutation semantics. It integrates with OrangeFS distributed-directory handling by passing directory data handle counts and split threshold in the mkdir attrs.

Risks: the recursive parent creation path uses `dirname` on multiple mutable buffers and then reuses `parentdir_ptr`; pointer lifetime and mutation order are subtle. Numeric option parsing with `sscanf` only checks parse success, not positivity or semantic constraints between initial and max dirdata. `PVFS_ATTR_SYS_ALL_SETABLE` is used with mostly zeroed attrs, which may unintentionally set fields beyond the intended subset. Some allocation and resolve failures leak earlier allocations or skip finalize. Existing-directory behavior simply reports `PVFS_sys_mkdir` errors rather than matching GNU `mkdir -p` idempotence.

Test signals: create one and many directories, exceed 100 args, mode default with umask, explicit octal mode, invalid mode text, `-p` for missing nested parents, `-p` when target already exists, root path rejection, invalid pvfstab path, permission-denied, `--init-num-dirdata`, `--max-num-dirdata`, and `--split-size` propagation verified through stat/fsck metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-mkspace.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-mkspace.c

Purpose: `pvfs2-mkspace.c` creates or removes OrangeFS storage spaces and collections by wrapping the lower-level `mkspace.h` helpers. It is used during filesystem provisioning and destructive cleanup.

Important APIs, types, and functions: `options_t` captures defaults flag, verbosity, collection id/name, root handle, collection-only mode, delete-storage mode, handle ranges, and data/metadata storage paths. `parse_args` handles short and long options, `print_options` reports the effective config, `print_help` documents defaults, and `main` calls either `pvfs2_mkspace` or `pvfs2_rmspace`. Default ranges are `4-2147483650` for metadata and `2147483651-4294967297` for data, with default collection name `pvfs2-fs`.

Control flow: with no args the tool prints help and exits failure. Parsing supports `--data-space`, `--meta-space`, `--coll-id`, `--coll-name`, `--root-handle`, `--delete-storage`, `--meta-handle-range`, `--data-handle-range`, `--add-coll`, `--defaults`, version, help, and verbose. If defaults are requested, selected fields are overwritten with static defaults. The program prints options, validates that data space, metadata space, collection id, and at least one handle range are present, then dispatches to remove or create.

State and persistence: this is a persistent storage-space mutator. `pvfs2_mkspace` creates Trove/storage directories and collection metadata, while `pvfs2_rmspace` removes them when `--delete-storage` is passed. `--add-coll` limits operation to collection creation/removal inside an existing storage space.

Dependencies and integration points: it depends on `mkspace.h` and the storage backend implementation behind `pvfs2_mkspace`/`pvfs2_rmspace`. Generated configuration from `pvfs2-genconfig` must agree with collection id, collection name, root handle, handle ranges, and storage paths used here.

Risks: `--delete-storage` is explicitly unrecoverable, but there is no confirmation prompt. `--defaults` does not set data or metadata storage paths or collection id, so it is not a full standalone default mode. The create path prints `opts.collection_only(%d).` as debug noise. Numeric parsing uses `strtoull`/`strtoul` without end-pointer validation, so malformed values can become zero. `strncpy` calls may leave nonterminated strings if optarg length reaches `PATH_MAX - 1` in some paths. A missing root handle defaults to `PVFS_HANDLE_NULL`, which may or may not be valid depending on helper behavior.

Test signals: dry-run style tests should isolate temp data/meta spaces. Cover missing required paths, defaults plus explicit required options, create storage, add collection, delete collection-only, delete full storage, invalid collection id/root handle/range text, long path truncation, verbose mode, and compatibility with configs emitted by `pvfs2-genconfig`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-mkspace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perf-mon-example.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perf-mon-example.c

Purpose: `pvfs2-perf-mon-example.c` is an interactive/example performance monitor that repeatedly samples OrangeFS I/O-server counters and prints bandwidth and operation counters to stdout.

Important APIs, types, and functions: `struct options` stores mount point, history, and key count. Counter access is implemented by matrix macros such as `READ`, `WRITE`, `METADATA_READ`, `REQUESTS`, `CREATES`, `GETATTRS`, and `VALID_FLAG`. The code uses `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, `PVFS_util_refresh_credential`, `PVFS_mgmt_perf_mon_list`, and `PVFS_mgmt_map_addr`.

Control flow: parsing requires `-m fs_mount_point`, optionally accepts `-h history`, `-k keys`, and `-v` version, and appends a slash to the mount path for later resolution. Main defaults history to 10, initializes OrangeFS, resolves the mount, generates credentials, counts I/O servers, allocates a per-server performance matrix plus `next_id` and end-time arrays, and builds the I/O-server address array. It then loops forever: refresh credential, request up to `MAX_KEY_CNT` counter keys with `PVFS_mgmt_perf_mon_list`, print server headers, compute data read/write MB/s from byte deltas and sample intervals, print other counters across the history window, flush, and sleep five seconds.

State and persistence: no persistent state is written. Runtime state is the rolling `next_id_array`, returned matrix samples, and credential refresh state. The process is intentionally long-running.

Dependencies and integration points: it samples management performance counters defined by `pvfs2-mgmt.h`/`PINT_PERF_*` and is useful for manual diagnostics or as sample code for external monitoring integrations. It depends on a mounted or configured filesystem path to discover I/O servers.

Risks: the code after the infinite loop, including `PVFS_sys_finalize`, is unreachable. Allocations are not freed. The `-k` option is parsed but not actually used because `key_cnt` is reset to `MAX_KEY_CNT`. Bandwidth calculation can divide by zero if timestamps match. Counter matrix layout is encoded in macros and must stay aligned with `PVFS_mgmt_perf_mon_list` key ordering. It prints indefinitely and has no signal cleanup. History values are not bounded before allocation.

Test signals: run against a small test filesystem with one and multiple I/O servers, verify valid/invalid mount handling, history default and explicit values, counter matrix dimensions, credential refresh over long runtime, zero-read/write shortcuts, timestamp edge cases, and management failures. Static tests should check key ordering against `pvfs2-mgmt.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perf-mon-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perf-mon-snmp.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perf-mon-snmp.c

Purpose: `pvfs2-perf-mon-snmp.c` adapts OrangeFS performance counters to a simple stdin/stdout protocol suitable for SNMP pass/persist style polling. It maps fixed OIDs to management performance counters and returns a type plus value.

Important APIs, types, and functions: `struct MGMT_perf_iod` maps OID string, SNMP type (`INTEGER` or `COUNTER`), `PINT_PERF_*` key number, and name. `key_table` defines OIDs under `.1.3.6.1.4.1.7778`. `struct options` stores either mount point or explicit server address. The tool uses `PVFS_util_init_defaults`, `PVFS_util_gen_credential_defaults`, `PVFS_util_get_default_fsid`, `BMI_addr_lookup`, `PVFS_util_resolve`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, and `PVFS_mgmt_perf_mon_list`.

Control flow: parsing requires either `-m fs_mount_point` or `-s bmi_address_string`. With `-s`, the program uses the default fsid and a single looked-up BMI address. With `-m`, it resolves the mount and samples all I/O servers. It counts keys from `key_table`, allocates a one-sample matrix and tracking arrays, then loops reading commands from stdin. `PING` returns `PONG`. `GET` reads the next line as an OID, looks it up in `key_table`, and returns `NONE` if unknown. For valid OIDs it refreshes the performance snapshot if the cached snapshot is older than 60 seconds, then prints the SNMP type and unsigned value.

State and persistence: no files are written. The process caches one performance snapshot for up to 60 seconds using `snaptime`, `perf_matrix`, `next_id_array`, and `end_time_ms_array`.

Dependencies and integration points: this utility is meant to be driven by an SNMP daemon. The OID table comments say it must match `include/pvfs2-mgmt.h`, so key-number drift is a direct integration risk. It can operate from an OrangeFS mount point or a raw BMI server address.

Risks: `returnValue` is initialized to zero for each command and only assigned inside the snapshot-refresh block; valid GETs within 60 seconds after a refresh can return zero instead of cached matrix data. Only `srv = 0` is returned even when multiple I/O servers are sampled. The program does not refresh credentials inside the loop. Memory and sysint cleanup after the infinite loop are unreachable. The command buffer is fixed at 256 bytes and longer OIDs/commands are not robustly drained. Error output from `PVFS_perror` may interfere with SNMP expectations if written to stdout by dependencies.

Test signals: simulate pass/persist input with `PING`, unknown commands, unknown OIDs, valid OIDs before and after the 60-second cache window, mount-discovered multi-server mode, explicit server mode, invalid BMI address, management failure, and key table alignment with `PINT_PERF_*` values. A regression test should specifically catch repeated valid GET returning zero due to cache logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perf-mon-snmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perror.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perror.c

Purpose: `pvfs2-perror.c` is a small diagnostic utility that translates a numeric OrangeFS/PVFS error code into the standard `PVFS_perror` message.

Important APIs, types, and functions: `struct options` stores one `error_code`. `parse_args` accepts `-v` for version and `-h` for help, requires exactly one positional integer, and parses it with `sscanf`. `main` prints `Error code N` and calls `PVFS_perror("", -N)`. The only OrangeFS dependency is `pvfs2.h` for `PVFS_perror` and version wiring.

Control flow: main delegates all validation to `parse_args`. Help and version exit directly. If parsing succeeds, the utility prints to stderr and returns success. The input sign convention is inverted before calling `PVFS_perror`, so users enter positive errno-like numbers while the OrangeFS API receives negative PVFS status codes.

State and persistence: no state is read or written except command-line input and stderr output.

Dependencies and integration points: this is useful in scripts and admin sessions that receive numeric negative PVFS return values. It depends on the library error table compiled into the OrangeFS client library.

Risks: allocated options are not freed, though the process is short-lived. The usage text does not explain sign convention. `sscanf("%d")` accepts prefixes such as `12abc` as valid. It prints to stderr even on normal diagnostic success, which is conventional for `perror` but can surprise scripts.

Test signals: verify `-h`, `-v`, missing argument, extra arguments, nonnumeric input, positive values matching known PVFS errors, and behavior if users pass an already-negative code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perror.c -->
