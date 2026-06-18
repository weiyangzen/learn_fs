# subset-b-009620 research

Grouped source research for the requested Impacket files. Each section preserves the exact source path for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ese.py -->
# sources/user-network-fs/impacket/impacket/ese.py

## Purpose
`ese.py` is a focused Microsoft Extensible Storage Engine database parser, primarily aimed at reading `NTDS.dit`-style ESE files rather than implementing a full read/write ESE stack. It defines the binary structures, catalog walker, page/tag decoder, table cursor, and record materialization logic needed by higher-level code to open an ESE database, inspect its catalog, open a table, and iterate decoded rows.

## Important APIs, Types, and Functions
- Constants model ESE file type, database state, page flags, tag flags, catalog object types, column types, code pages, and page/tag layout differences. `ColumnTypeToName`, `ColumnTypeSize`, and `StringCodePages` drive record decoding.
- `ESENT_JET_SIGNATURE`, `ESENT_DB_HEADER`, `ESENT_PAGE_HEADER`, `ESENT_ROOT_HEADER`, `ESENT_BRANCH_HEADER`, `ESENT_BRANCH_ENTRY`, `ESENT_LEAF_HEADER`, `ESENT_LEAF_ENTRY`, `ESENT_SPACE_TREE_HEADER`, `ESENT_SPACE_TREE_ENTRY`, `ESENT_INDEX_ENTRY`, `ESENT_DATA_DEFINITION_HEADER`, and `ESENT_CATALOG_DATA_DEFINITION_ENTRY` are `impacket.structure.Structure` subclasses for on-disk records.
- `ESENT_PAGE_HEADER.__init__` chooses the header layout based on database `Version`, `FileFormatRevision`, and `PageSize`, including extended Windows 7+ fields for pages larger than 8192 bytes.
- `ESENT_PAGE` wraps one parsed page, computes tag counts for old and newer page formats, exposes `iterDataTagNums()`, `getTag()`, `printFlags()`, and `dump()`.
- `ESENT_DB` is the main public class. Construction mounts the database, reads the header, parses the catalog, and exposes `printCatalog()`, `openTable()`, `getNextRow()`, `getPage()`, and `close()`.
- `getUnixTime()` converts Windows FILETIME-like timestamps to Unix seconds.

## Control Flow
`ESENT_DB.__init__` calls `mountDB()`, which opens either a local file or a remote file-like object, reads page `-1` as the database header, sets page size and total page count, then recursively parses the catalog from fixed page 4. Catalog parsing descends branch pages via child page numbers and adds leaf table/column/index/long-value entries to `self.__tables`. `openTable()` finds the table catalog entry, descends from the table father data page to a leaf, and returns a mutable cursor dictionary. `getNextRow()` advances the cursor over page tags, follows `NextPageNumber` links, and calls `__tagToRecord()` to decode each leaf record.

`__tagToRecord()` is the central record decoder. It reads the data-definition header, walks catalog columns, extracts fixed-size fields, variable-size fields, and tagged fields, then decodes text by code page and scalar values by `struct.unpack`. Tagged values are parsed lazily once per record and stored in an ordered map of identifier to offset/length/flags.

## State and Persistence Behavior
The parser maintains local mutable state: the file handle, database header, total page count, catalog table map, current table name during catalog parsing, and cursor dictionaries for table iteration. It reads ESE data from disk or a remote file-like object but does not write to the database. It may print catalog/page dumps to stdout and emits diagnostics through `impacket.LOG`. `TABLE_CURSOR` is a module-level dictionary reused by `openTable()`, so multiple cursors can share the same backing object unless callers copy it; this is an important statefulness risk.

## Dependencies and Integration Points
The module depends on `impacket.structure.Structure` and `hexdump`, `impacket.LOG`, `struct.unpack`, `binascii.hexlify`, `six.b`, and `collections.OrderedDict`. It integrates with callers that need offline extraction from ESE databases, especially Active Directory database readers. Remote mode expects the `fileName` argument to be a file-like object with `open()`, `seek()`, `read()`, and `close()`.

## Risks and Edge Cases
- Long values are explicitly unsupported in page dumping and mostly skipped in normal parsing.
- Multi-value tagged data is returned as raw hex rather than a structured list.
- Compressed tagged columns are logged as unsupported and returned as `None`.
- `getPage()` keeps reading until a full page is available and can loop badly on a truncated stream that keeps returning empty bytes.
- `TABLE_CURSOR` is shared module state, creating possible cursor interference.
- Many parsing assumptions are NTDS-oriented and may not hold for arbitrary ESE databases.
- Unsupported code pages, unknown catalog types, or malformed tag arrays can raise exceptions.

## Test Signals
Good coverage would mount representative ESE/NTDS fixtures for old 8 KiB pages and newer 16/32 KiB page formats, verify catalog tables/columns, iterate rows across linked leaf pages, decode fixed/variable/tagged text and numeric columns, and assert behavior for compressed/multivalue/long-value fields. Fuzz/truncation tests should exercise malformed headers, short pages, invalid tag offsets, and unsupported code pages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ese.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/__init__.py -->
# sources/user-network-fs/impacket/impacket/examples/__init__.py

## Purpose
This package initializer applies compatibility monkeypatches for example scripts. It weakens Python SSL defaults to support legacy or insecurely configured targets and adds a missing `readline.backend` attribute for environments whose `readline` module does not expose it.

## Important APIs, Types, and Functions
- `_insecure_create_default_context()` wraps the original SSL default context factory, lowers the minimum TLS version to `ssl.TLSVersion.MINIMUM_SUPPORTED`, enables `ALL:@SECLEVEL=0` ciphers, disables hostname checking, and sets `CERT_NONE`.
- `monkeypatch_ssl_create_default_context()` stores the original function as `ssl._create_default_context` and replaces `ssl.create_default_context`.
- `monkeypatch_readline_backend()` sets `readline.backend = "readline"` when absent.

## Control Flow
The module executes both monkeypatch functions at import time. The SSL monkeypatch only runs if `ssl.create_default_context` is not already the insecure wrapper. The readline patch only runs if the attribute is missing.

## State and Persistence Behavior
The module mutates process-global `ssl` and `readline` state. The change persists for the lifetime of the Python process and affects all later code using `ssl.create_default_context`, not only Impacket examples. It logs debug messages through `impacket.LOG` when patching occurs.

## Dependencies and Integration Points
It depends on Python `ssl` and `readline`, with delayed `impacket.LOG` import for debug logs. Any example importing `impacket.examples` receives these patched defaults.

## Risks and Edge Cases
The SSL patch disables certificate verification and hostname checking globally, which is useful for relaying to old systems but risky in any code path expecting normal TLS validation. The code relies on private-ish `ssl._create_default_context` naming to preserve the original function.

## Test Signals
Tests should import the package in a fresh interpreter, assert `ssl.create_default_context` is replaced once, verify generated contexts have `CERT_NONE` and no hostname check, and confirm re-imports are idempotent. A compatibility test can assert `readline.backend` exists after import.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ldap_shell.py -->
# sources/user-network-fs/impacket/impacket/examples/ldap_shell.py

## Purpose
`ldap_shell.py` implements an interactive LDAP command shell used by ntlmrelayx and related tooling after a relayed LDAP/LDAPS session is established. It exposes administrative and offensive Active Directory operations such as adding computers/users, changing passwords, modifying DACLs, configuring RBCD, shadow credentials, account flags, searches, LAPS reads, and DirSync.

## Important APIs, Types, and Functions
- `LdapShell(cmd.Cmd)` is the only exported class. It binds stdin/stdout/stderr to a `TcpShell`-style object and stores an `ldap3.Connection` plus `ldapdomaindump` dumper.
- Security descriptor helpers `create_empty_sd()` and `create_allow_ace()` build Impacket LDAP security descriptors and full-control ACEs.
- Command methods include `do_add_computer`, `do_rename_computer`, `do_add_user`, `do_add_user_to_group`, `do_change_password`, `do_clear_rbcd`, `do_dump`, `do_start_tls`, `do_disable_account`, `do_enable_account`, `do_search`, `do_set_dontreqpreauth`, `do_get_user_groups`, `do_get_group_users`, `do_get_laps_password`, `do_grant_control`, `do_set_rbcd`, `do_set_shadow_creds`, `do_clear_shadow_creds`, `do_whoami`, `do_dirsync`, `do_exit`, and `do_help`.
- `search()` and `get_dn()` are utility methods used by multiple commands.

## Control Flow
`onecmd()` delegates to `cmd.Cmd.onecmd()` inside broad exception handling so shell errors are printed and logged without killing the session. Each `do_*` method parses arguments with `shlex.split`, performs LDAP searches or modifications, and prints success/error details to the TCP shell. Mutating operations generally search for target DNs/SIDs first, construct descriptors or attribute changes, call `client.modify()`/`client.add()`/Microsoft LDAP extensions, then check `client.result`.

## State and Persistence Behavior
The shell mutates remote Active Directory state: user/computer objects, group membership, `unicodePwd`, `userAccountControl`, `nTSecurityDescriptor`, `msDS-AllowedToActOnBehalfOfOtherIdentity`, `msDS-KeyCredentialLink`, and potentially the output of `domainDump()`. Local state includes shell streams, prompt, `loggedIn`, `last_output`, and references to the LDAP client and dumper. Shadow credentials export generated PFX files with random names and passwords in the current working directory.

## Dependencies and Integration Points
It depends on `cmd`, `ldap3`, `ldap3.protocol.microsoft.security_descriptor_control`, `ldap3.utils.conv.escape_filter_chars`, Impacket LDAP types, `impacket.examples.ntlmrelayx.utils.shadow_credentials`, `uuid`, and `impacket.LOG`. It is launched by `LDAPAttack` in interactive mode and assumes a live authenticated LDAP client plus a `domain_dumper.root`.

## Risks and Edge Cases
- Several mutating commands warn about LDAPS but do not always return immediately after the warning, so a denied LDAP modify can still be attempted.
- Some argument validation has indexing bugs or inconsistent length checks, for example `do_set_rbcd` rejects one or two arguments incorrectly yet later indexes two arguments.
- Commands print generated passwords and certificate passwords to the shell transcript.
- Broad exception handling keeps the shell alive but can hide partial mutations.
- LDAP filters are generally escaped for user-provided SAM names, but some filters and DN fragments are built directly from inputs.
- Security descriptor replacement is high-impact and may clobber concurrent changes if stale descriptors are used.

## Test Signals
Unit tests can use a fake `ldap3.Connection` to verify exact searches, modify payloads, controls, and error handling for each command. Integration tests need an AD lab to validate LDAPS add-user/add-computer, RBCD write/clear, shadow credential write/clear, DACL modification, LAPS read permission behavior, and DirSync paging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ldap_shell.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/logger.py -->
# sources/user-network-fs/impacket/impacket/examples/logger.py

## Purpose
`logger.py` centralizes example-script logging configuration for Impacket. It adds a root `StreamHandler` with Impacket-specific prefixes and optional timestamps, supports ntlmrelayx identity prefixes, and sets the logging level for normal or debug output.

## Important APIs, Types, and Functions
- `ImpacketFormatter` formats records as `bullet identity message`, mapping INFO to `[*]`, DEBUG to `[+]`, WARNING to `[!]`, and errors/others to `[-]`.
- `ImpacketFormatterTimeStamp` extends that format with a timestamp and formats time as `%Y-%m-%d %H:%M:%S`.
- `init(ts=False, debug=False)` installs the handler, adds `IdentityFilter`, sets root level to DEBUG or INFO, logs the installation path in debug mode, and silences `impacket.smbserver` down to ERROR in non-debug mode.

## Control Flow
Callers invoke `init()` early in a script. The function constructs a `logging.StreamHandler(sys.stdout)`, selects a formatter based on `ts`, attaches the identity filter, adds it to the root logger, and adjusts logger levels.

## State and Persistence Behavior
The function mutates global logging state by adding handlers to the root logger. Repeated calls add additional handlers because no deduplication is performed. Formatter methods mutate transient `LogRecord` attributes `bullet` and `identity`.

## Dependencies and Integration Points
It depends on Python `logging`, `sys`, `impacket.version`, and `impacket.examples.ntlmrelayx.utils.identity_log.IdentityFilter`. It is used by Impacket command-line examples to get consistent console output.

## Risks and Edge Cases
Repeated initialization can duplicate log lines. Formatting assumes root records can safely receive dynamic attributes. The identity filter dependency couples generic example logging to ntlmrelayx utility code.

## Test Signals
Tests should assert prefix mapping by level, timestamp rendering, identity preservation/defaulting, root logger level changes, smbserver logger suppression in non-debug mode, and duplicate handler behavior on repeated `init()` calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/logger.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/mssqlshell.py -->
# sources/user-network-fs/impacket/impacket/examples/mssqlshell.py

## Purpose
`mssqlshell.py` implements an interactive SQL Server shell over an Impacket TDS/MSSQL client. It supports arbitrary SQL execution, linked-server traversal, impersonation, xp_cmdshell and SQL Agent execution, local shell commands, file upload/download through SQL Server features, and database/security enumeration.

## Important APIs, Types, and Functions
- `SQLSHELL(cmd.Cmd)` is the main class. It accepts an SQL client object, an optional TCP shell, and a `show_queries` flag.
- Prompt and output helpers: `set_prompt()`, `postcmd()`, `print_replies()`, and `sql_query()`.
- Interactive command methods include `do_exec_as_login`, `do_exec_as_user`, `do_use_link`, `do_shell`, `do_download`, `do_upload`, `do_xp_dirtree`, `do_xp_cmdshell`, `do_sp_start_job`, `do_lcd`, `do_enable_xp_cmdshell`, `do_disable_xp_cmdshell`, `do_enum_links`, `do_enable_rpc`, `do_disable_rpc`, `do_enum_users`, `do_enum_db`, `do_enum_owner`, `do_enum_impersonate`, `do_enum_logins`, `default`, `emptyline`, and `do_exit`.

## Control Flow
Construction binds the shell to normal stdio or a `TcpShell`, stores the SQL client, initializes the linked-server stack `self.at`, and derives a prompt from `system_user`, `current_user`, and `currentDB`. `sql_query()` wraps SQL through nested `EXEC (...) AT linked_server` calls for the current linked-server stack, optionally prints the query, then delegates to `self.sql.sql_query()`. Most `do_*` commands build SQL text, run it, and print replies/rows.

## State and Persistence Behavior
Local state includes the SQL client, prompt state, `show_queries`, current linked-server stack, current local directory, and optional TCP shell. Remote state can be heavily mutated: enabling/disabling `xp_cmdshell`, changing RPC Out on linked servers, creating SQL Agent jobs, executing OS commands, uploading files via base64 chunks and `certutil`, deleting temporary `.b64` files, and changing execution context. Downloads write local files; uploads read local files and create remote files.

## Dependencies and Integration Points
It depends on `cmd`, `os`, `sys`, `hashlib`, `base64`, `shlex`, and an Impacket MSSQL client with `sql_query`, `printReplies`, `printRows`, `rows`, `colMeta`, and `currentDB`. It is launched by `MSSQLAttack` for interactive ntlmrelayx sessions.

## Risks and Edge Cases
- SQL strings are assembled by interpolation with minimal quoting, so shell inputs can break query syntax or execute unintended SQL.
- Many commands catch all exceptions and silently pass, which obscures failures.
- File upload depends on `xp_cmdshell`, Windows `certutil`, echo chunking, permissions, and MD5 output format.
- `do_download` requires bulk admin permission and assumes returned `BulkColumn` data can be hex-decoded from the client representation.
- Linked-server wrapping manually escapes single quotes but can still be fragile for complex commands.

## Test Signals
Fake SQL-client tests should verify query construction for impersonation, linked-server nesting, xp_cmdshell, file upload chunks, and enumeration commands. Integration tests need SQL Server fixtures with and without xp_cmdshell, bulk operations, linked servers, and impersonation permissions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/mssqlshell.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/__init__.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/__init__.py

## Purpose
This is an empty package marker for the `impacket.examples.ntlmrelayx` package. It enables imports of ntlmrelayx clients, attacks, servers, utilities, and related modules.

## Important APIs, Types, and Functions
No runtime APIs, classes, functions, or constants are defined.

## Control Flow
Importing the package executes no behavior beyond normal package initialization.

## State and Persistence Behavior
No local or remote state is created or mutated.

## Dependencies and Integration Points
It is an integration point for Python package discovery and relative imports under `impacket.examples.ntlmrelayx`.

## Risks and Edge Cases
Behavioral risk is minimal. The main compatibility risk is accidental addition of import-time side effects here, which would affect every ntlmrelayx import.

## Test Signals
Import tests should confirm `impacket.examples.ntlmrelayx` imports cleanly and package submodules remain discoverable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/__init__.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/__init__.py

## Purpose
This module defines the base class and dynamic plugin loader for ntlmrelayx protocol attacks. It discovers attack modules in the package, imports them, extracts their advertised attack classes, and registers them by protocol name in `PROTOCOL_ATTACKS`.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACKS` is the global registry mapping protocol/plugin names to attack classes.
- `_wrap_run_with_identity()` decorates attack `run()` methods with identity logging context when target and relay client information are available.
- `ProtocolAttack(Thread)` is the base class. It stores `config`, `client`, parsed `domain`, parsed `username`, optional `target`, and optional `relay_client`; subclasses are daemon threads.
- `ProtocolAttack.__init_subclass__()` wraps subclass-defined `run()` methods automatically.

## Control Flow
On import, the module scans files under `impacket.examples.ntlmrelayx.attacks`, imports each non-`__` Python file, reads `PROTOCOL_ATTACK_CLASS` or `PROTOCOL_ATTACK_CLASSES`, then registers each class under every value in its `PLUGIN_NAMES`. Import/logging errors are swallowed into debug logs so one broken plugin does not prevent loading others.

## State and Persistence Behavior
Global registry state is populated at import time. Each attack instance is a daemon `Thread`, although subclasses often call `run()` directly in relay control flow. The identity wrapper affects logging context only during `run()`.

## Dependencies and Integration Points
It depends on `importlib.resources.files`, `os`, `sys`, `threading.Thread`, `impacket.LOG`, and `identity_context`. It is imported by all attack modules and by ntlmrelayx orchestration to find the right attack for a relayed protocol.

## Risks and Edge Cases
- Import-time dynamic discovery can trigger side effects in every attack module.
- Registration silently ignores malformed plugins except for debug logs.
- `ProtocolAttack.__init__` assumes usernames contain `domain/user`; a malformed identity without `/` raises.
- Automatic `run()` wrapping can surprise subclasses that depend on exact function attributes.

## Test Signals
Tests should verify registry population, multiple-class registration, malformed plugin handling, identity-context formatting, daemon thread setup, and username/domain parsing error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/dcsyncattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/dcsyncattack.py

## Purpose
This module declares a `DCSYNCAttack` plugin name for ntlmrelayx, but its `run()` method is currently a no-op. It appears to be a placeholder or compatibility shim rather than an implemented DCSync attack path.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "DCSYNCAttack"` advertises the plugin class.
- `DCSYNCAttack(ProtocolAttack)` sets `PLUGIN_NAMES = ["DCSYNC"]`.
- `run()` immediately returns.

## Control Flow
Dynamic plugin loading imports this module and registers `DCSYNC` to `DCSYNCAttack`. Running the attack performs no operations.

## State and Persistence Behavior
No state is mutated by `run()`. The module imports `RemoteOperations`, `SAMHashes`, and `NTDSHashes` from `secretsdump`, but they are unused.

## Dependencies and Integration Points
It depends on the ntlmrelayx attack base and secretsdump classes. Its main integration role is registry exposure through `PROTOCOL_ATTACK_CLASS`.

## Risks and Edge Cases
The risk is operator confusion: the plugin name suggests DCSync behavior, but the implementation does nothing. Unused imports increase import cost and can fail if secretsdump dependencies break.

## Test Signals
A registry test should confirm the `DCSYNC` plugin maps to this class. A behavioral test should assert `run()` returns without client calls until real functionality is implemented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/dcsyncattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattack.py

## Purpose
`httpattack.py` dispatches relayed HTTP/HTTPS sessions to specific HTTP-based attack mixins: AD CS certificate enrollment, SCCM policy secret retrieval, SCCM distribution point file dumping, or a minimal default root-page dump.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "HTTPAttack"` advertises the plugin.
- `HTTPAttack(ProtocolAttack, ADCSAttack, SCCMPoliciesAttack, SCCMDPAttack)` registers `PLUGIN_NAMES = ["HTTP", "HTTPS"]`.
- `run()` checks `config.isADCSAttack`, `config.isSCCMPoliciesAttack`, and `config.isSCCMDPAttack` to call the corresponding mixin `_run()`.

## Control Flow
When ntlmrelayx executes this attack, `run()` selects one configured mode in priority order: ADCS, SCCM policies, SCCM DP. If none are configured, it performs a GET `/`, prints the HTTP status/reason, reads the body, and prints it.

## State and Persistence Behavior
The dispatcher itself keeps no additional state. The selected mixin may write certificate files, SCCM loot directories, policies, or downloaded files. The default path only reads a response and prints to stdout.

## Dependencies and Integration Points
It depends on the attack base and HTTP mixins from `attacks/httpattacks`. It assumes `self.client` has `request()` and `getresponse()` methods compatible with `http.client`-style clients.

## Risks and Edge Cases
Only one attack mode runs because of `if/elif` ordering. The default branch prints raw response bodies directly and does not write deterministic loot. Misspelled config attributes would raise at runtime.

## Test Signals
Tests can use a fake client and config to assert dispatch order, request paths, and that each mode invokes the intended mixin method exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/__init__.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/__init__.py

## Purpose
This file is an empty package marker for HTTP-specific ntlmrelayx attack mixins.

## Important APIs, Types, and Functions
No APIs, classes, functions, or constants are defined.

## Control Flow
Importing the package performs no runtime behavior.

## State and Persistence Behavior
No state is created or mutated.

## Dependencies and Integration Points
The package groups `adcsattack.py`, `sccmdpattack.py`, and `sccmpoliciesattack.py` for import by `HTTPAttack`.

## Risks and Edge Cases
Risk is minimal. Keeping this file side-effect-free is important because it is imported by HTTP attack code.

## Test Signals
Import tests should confirm the package imports and submodules are discoverable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/adcsattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/adcsattack.py

## Purpose
`adcsattack.py` implements the HTTP Web Enrollment variant of an AD CS relay attack. It can enumerate certificate templates from `/certsrv/certrqxt.asp` or submit a CSR to `/certsrv/certfnsh.asp`, retrieve the issued certificate, and write a PKCS#12 file for later authentication.

## Important APIs, Types, and Functions
- `ELEVATED` is a module-level list used to skip repeated certificate requests for the same username.
- `ADCSAttack._run()` performs template enumeration or certificate request/retrieval.
- Static helpers `generate_csr()`, `generate_pfx()`, and `generate_certattributes()` build the CSR, PKCS#12 payload, and AD CS request attributes.
- `enum_templates()` parses `<Option Value="...">` rows from the web enrollment template page.
- `_extract_certificate_identity()` pulls CN, UPN OtherName, or DNS SAN from a certificate.
- `_sanitize_filename()` normalizes output filenames.

## Control Flow
`_run()` generates a 4096-bit RSA key, skips if the username is already in `ELEVATED`, optionally enumerates templates, selects a template (`Machine` for machine accounts and `User` otherwise by default), builds a CSR and form body, POSTs to `certfnsh.asp`, extracts `ReqID`, GETs `certnew.cer`, converts the certificate to a cryptography object, serializes a PFX, and writes it into `config.lootdir`. On file write failure it logs base64 PFX data instead.

## State and Persistence Behavior
State is held in the global `ELEVATED` list and in generated private key/certificate objects. Persistent output is a `.pfx` file under `config.lootdir`, or base64 material in logs if writing fails. The attack mutates the AD CS CA by creating a certificate request and issuing a certificate.

## Dependencies and Integration Points
It depends on `OpenSSL.crypto`, `cryptography.x509`, `cryptography.hazmat.primitives.serialization.pkcs12`, `urllib.parse`, `re`, `base64`, `os`, and `impacket.LOG`. It is mixed into `HTTPAttack` and assumes an HTTP client compatible with `request()`/`getresponse()`.

## Risks and Edge Cases
- Global `ELEVATED` is process-wide and keyed only by username, not target CA or template.
- HTML parsing is regex-based and fragile to localized or changed Web Enrollment pages.
- PFX is serialized without encryption.
- Alternate names can create certificates for identities other than the relayed username.
- If `config.lootdir` creation fails, certificate material is logged.

## Test Signals
Tests should fake HTTP responses for template enumeration, successful ReqID extraction, failed status, missing ReqID, certificate identity extraction, filename sanitization, and PFX writing fallback. Integration tests need an AD CS Web Enrollment lab with user and machine templates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/adcsattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/sccmdpattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/sccmdpattack.py

## Purpose
`sccmdpattack.py` implements an SCCM Distribution Point relay attack that indexes packages exposed under `sms_dp_smspkg$`, builds a tree of package contents, and downloads files matching configured extensions or explicit URLs.

## Important APIs, Types, and Functions
- `print_tree()` writes a directory tree representation to an output stream.
- `PackageIDsRetriever(HTMLParser)` extracts package IDs from Datalib anchor tags.
- `FilesAndDirsRetriever(HTMLParser)` extracts directory/file links and associated previous text markers.
- `SCCMDPAttack._run()` orchestrates indexing and download.
- `recursive_file_extract()`, `download_files()`, `download_target_files()`, `handle_packages()`, `recursive_package_directory_fetch()`, and `fetch_package_ids_from_datalib()` implement package traversal and download.

## Control Flow
`_run()` derives the distribution point URL from client port/host, creates a timestamped loot directory, normalizes extension filtering, optionally fetches package IDs from Datalib, then calls `download_target_files()`. Explicit file mode reads URLs from `config.SCCMDPFiles`; otherwise it handles every discovered package by recursively fetching directory listings, writing `index.txt`, selecting matching files, creating package directories, and downloading each file.

## State and Persistence Behavior
Local state includes `distribution_point`, `loot_dir`, `package_ids`, and normalized config extension lists. Persistent output is a timestamped `*_sccm_dp_loot` directory with `index.txt` and downloaded package files under `packages/<package_id>/`. Remote state is read-only HTTP access.

## Dependencies and Integration Points
It depends on `os`, `json` (unused), `urllib.parse`, `HTMLParser`, `datetime`, and `impacket.LOG`. It is mixed into `HTTPAttack` and assumes `self.client.host`, `self.client.port`, `request()`, and `getresponse()`.

## Risks and Edge Cases
- HTML parsing depends on IIS directory listing shape and previous text containing `<dir>`.
- Recursive traversal uses a fixed max depth of 7; deeper packages are marked but not traversed.
- Output filenames are derived from URL path fragments and may collide.
- No HTTP status checks are performed before parsing/downloading bodies.
- Extension matching is suffix-based and case-sensitive.

## Test Signals
Unit tests should feed sample Datalib and directory HTML to the parsers, verify recursion depth handling, extension filtering, explicit URL mode, output path construction, and download request headers. Integration tests need an SCCM DP fixture or captured HTTP directory listings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/sccmdpattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/sccmpoliciesattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/sccmpoliciesattack.py

## Purpose
`sccmpoliciesattack.py` implements an SCCM Management Point relay attack that registers a spoofed ConfigMgr client, requests machine policy assignments, identifies secret policies, decrypts them, deobfuscates secret blobs, and writes credentials/scripts/policy material to a loot directory.

## Important APIs, Types, and Functions
- XML templates define client registration, message headers, policy request bodies, and reporting payloads.
- Crypto helpers: `create_private_key()`, `create_certificate()`, `SCCM_sign()`, `build_MS_public_key_blob()`, `mscrypt_derive_key_sha1()`.
- Payload helpers: `encode_UTF16_strip_BOM()`, `clean_junk_in_XML()`, `generate_registration_request_payload()`, and `generate_policies_request_payload()`.
- Decryption helpers: `decrypt_key_OEAP()`, `decrypt_key_RSA()`, `decrypt_body_triple_DES()`, `decrypt_body_AESCBC()`, `decrypt_secret_policy()`, `deobfuscate_secret_policy_blob()`.
- `parse_policies_flags()` maps SCCM policy bitmasks to labels.
- `SCCMPoliciesAttack._run()` orchestrates registration, policy request, secret filtering, and processing.
- `register_client()`, `request_policies()`, `request_policy()`, and `secret_policy_process()` perform HTTP exchanges and extraction.

## Control Flow
`_run()` builds a management point URL and timestamped loot directory, defaults the client name and sleep interval, generates a private key and self-signed ConfigMgr certificate, writes them under `device/`, registers the client via `CCM_POST`, extracts the assigned GUID, sleeps for server-side policy availability, requests policy assignments, writes `policies.json` and `policies.raw`, filters policies marked `SECRET`, fetches each secret policy, decrypts CMS/EnvelopedData, handles collection settings compression when needed, writes `policy.txt`, deobfuscates secret blobs, writes each secret blob and embedded PowerShell script, and logs Network Access Account credentials if found.

## State and Persistence Behavior
Persistent output is a timestamped `*_sccm_policies_loot` tree containing generated device certificate/key/GUID/client name, raw and parsed policy lists, decrypted policies, deobfuscated secret blobs, and embedded scripts. The attack mutates SCCM server state by registering a client identity. Local config fields are defaulted in-place for client name and sleep duration.

## Dependencies and Integration Points
It depends on `cryptography`, `pyasn1_modules.rfc5652`, `pyasn1.codec.der.decoder`, `zlib`, `xml.etree.ElementTree`, `datetime`, `sleep`, `base64`, `binascii`, and `impacket.LOG`. It is mixed into `HTTPAttack` and assumes an HTTP client with ConfigMgr verbs and standard response access.

## Risks and Edge Cases
- The default sleep is 180 seconds, making tests and operations slow.
- Parsing assumes multipart boundaries, UTF-16 payloads, XML shapes, and SCCM policy schemas.
- Decryption supports only selected RSA/OAEP key wrapping and 3DES/AES-CBC content OIDs.
- `deobfuscate_secret_policy_blob()` can reference an unset `block_cipher_algorithm` for unknown prefixes.
- Loot may include sensitive private keys, Network Access Account credentials, and scripts.
- Some `except` blocks swallow parse/decode failures and continue with partial output.

## Test Signals
Unit tests should cover payload generation signatures, UTF-16/BOM handling, policy flag parsing, multipart decompression, CMS decryption for supported OIDs, deobfuscation for known blob prefixes, and XML extraction of NAA credentials and embedded scripts. Integration tests need a lab SCCM MP or captured responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/sccmpoliciesattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/imapattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/imapattack.py

## Purpose
`imapattack.py` implements the IMAP/IMAPS relay attack. It searches or dumps a mailbox and writes selected messages as `.eml` files into the configured loot directory.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "IMAPAttack"` advertises the plugin.
- `IMAPAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["IMAP", "IMAPS"]`.
- `run()` performs mailbox selection, search/dump selection, message fetch, filename sanitization, file write, and logout.

## Control Flow
`run()` selects `config.mailbox` read-only and falls back to `INBOX` if selection fails. If `dump_all` is false, it searches `SUBJECT` or `BODY` for `config.keyword` and truncates results to `dump_max` when configured. If `dump_all` is true, it builds a numeric range up to `dump_max` or mailbox count. Each selected message is fetched with `RFC822`, sanitized into a `mail_<user>-<mailbox>_<id>.eml` filename, and written to `config.lootdir`.

## State and Persistence Behavior
The attack writes email files to local loot storage and logs progress. It does not modify the mailbox because it selects read-only, and it logs out at the end.

## Dependencies and Integration Points
It depends on `re`, `os`, `impacket.LOG`, and the attack base. It assumes an IMAP client with `select`, `search`, `fetch`, and `logout` methods.

## Risks and Edge Cases
- `rawdata` handling mixes bytes/strings depending on the IMAP library, and filenames also assume text usernames.
- File writing uses text mode even though RFC822 payloads can be bytes.
- Search result splitting on `' '` can fail for byte results or unusual server responses.
- No creation of `lootdir` is performed here.

## Test Signals
Tests should fake IMAP responses for mailbox fallback, keyword search, dump-all max behavior, fetch failures, filename sanitization, bytes-vs-string payloads, and logout execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/imapattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/ldapattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/ldapattack.py

## Purpose
`ldapattack.py` is the main LDAP/LDAPS relay attack implementation for ntlmrelayx. It can launch an interactive LDAP shell, validate relayed-user privileges, perform ACL-based DCSync escalation, add users/computers, add users to privileged groups, configure resource-based constrained delegation, add shadow credentials, dump domain/LAPS/gMSA/ADCS data, and create AD-integrated DNS records.

## Important APIs, Types, and Functions
- Global flags `dumpedDomain`, `dumpedAdcs`, `alreadyEscalated`, `alreadyAddedComputer`, and `delegatePerformed` prevent repeat actions in one process.
- `MSDS_MANAGEDPASSWORD_BLOB(Structure)` parses gMSA managed password blobs and slices current/previous password intervals.
- `LDAPAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["LDAP", "LDAPS"]`.
- Core mutators include `addComputer()`, `addUser()`, `addUserToGroup()`, `shadowCredentialsAttack()`, `delegateAttack()`, `aclAttack()`, `writeRestoreData()`, and `addDnsRecord()`.
- Discovery helpers include `validatePrivileges()`, `getUserInfo()`, `checkSecurityDescriptors()`, `aceApplies()`, and `dumpADCS()`.
- Module helpers `create_object_ace()`, `create_allow_ace()`, `create_empty_sd()`, `can_create_users()`, and `can_add_member()` build and inspect LDAP ACL structures.

## Control Flow
`run()` creates a `ldapdomaindump.domainDumper`, launches `LdapShell` in interactive mode if configured, optionally validates privileges by enumerating the relayed account's SID, recursive group SIDs, primary group, domain/OUs/Users container security descriptors, and interesting privileged groups. It then conditionally performs ACL attack, group escalation, LAPS dump, gMSA dump, ADCS dump, DNS record addition, computer addition, RBCD delegation for machine accounts, shadow credentials, and finally domain dump.

`aclAttack()` reads the domain DACL, appends replication rights ACEs for the chosen user SID, writes the descriptor back, re-reads the result, and stores restore JSON. `delegateAttack()` adds an ACE to `msDS-AllowedToActOnBehalfOfOtherIdentity`. `shadowCredentialsAttack()` appends a `KeyCredential` DN-binary value and exports PEM or PFX material. `addDnsRecord()` builds raw DNS node records and creates `dnsNode` objects, with a special WPAD bypass path.

## State and Persistence Behavior
Remote AD state may be changed extensively: new users/computers, group membership, domain DACL replication rights, RBCD descriptors, shadow credentials, DNS nodes, and LDAP StartTLS state. Local outputs include domain dump files under `config.lootdir`, LAPS/gMSA dump files in the working directory, ACL restore JSON, and shadow credential PEM/PFX files. Module-level globals make behavior process-wide rather than per target.

## Dependencies and Integration Points
The module depends on `ldap3`, `ldapdomaindump`, `dns.resolver`, `Cryptodome.Hash.MD4`, Impacket LDAP/security descriptor types, `impacket.uuid`, `impacket.structure`, `LdapShell`, `TcpShell`, and `shadow_credentials`. It is loaded by the ntlmrelayx attack registry and consumes many ntlmrelayx config flags.

## Risks and Edge Cases
- Global one-shot flags are not keyed by domain/target and can suppress legitimate operations across different relays.
- Many operations are high-impact and require cleanup; DNS creation logs cleanup instructions but does not automate cleanup.
- Generated credentials and certificate material are logged or written to local disk.
- Security descriptor writes can overwrite concurrent changes and may fail under constrained delegation/channel binding policies.
- Broad `except` blocks in dump paths can hide parse or permission errors.
- Privilege validation can be expensive in large domains.
- `addDnsRecord()` directly constructs binary DNS records and assumes SOA lookup and naming contexts are available.

## Test Signals
Unit tests should mock LDAP responses for privilege validation, ACE applicability, DACL mutation, restore-data writing, gMSA blob parsing/NT hash derivation, ADCS enrollment parsing, DNS record byte construction, and StartTLS fallback. Lab integration tests should cover ACL escalation, RBCD, shadow credentials, LAPS/gMSA reads, add-computer/add-user, and DNS record creation/cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/ldapattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/mssqlattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/mssqlattack.py

## Purpose
`mssqlattack.py` connects ntlmrelayx MSSQL relay sessions to either an interactive `SQLSHELL` or a configured list of SQL queries.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "MSSQLAttack"` advertises the plugin.
- `MSSQLAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["MSSQL"]`.
- `__init__()` creates a `TcpShell` when `config.interactive` is true.
- `run()` launches `SQLSHELL` in interactive mode, executes configured queries, or logs an error if no queries are configured.

## Control Flow
Interactive mode starts a local TCP shell, listens, wraps the relayed MSSQL client in `SQLSHELL`, and enters `cmdloop()`. Non-interactive mode iterates `config.queries`, logs each query, calls `client.sql_query()`, and prints replies and rows.

## State and Persistence Behavior
Local state is limited to the optional TCP shell. Remote SQL state depends entirely on provided queries or interactive shell actions. The module itself does not write files.

## Dependencies and Integration Points
It depends on `impacket.LOG`, `SQLSHELL`, `ProtocolAttack`, and `TcpShell`. It is registered by the attack loader for MSSQL relay targets.

## Risks and Edge Cases
Interactive mode exposes a local listener on loopback that remains active for the shell lifetime. Non-interactive queries are arbitrary and may mutate SQL Server state. No query timeout or transaction isolation is implemented here.

## Test Signals
Tests should assert interactive shell startup with a fake `TcpShell`, query iteration and output calls, and the no-query error path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/mssqlattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/rpcattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/rpcattack.py

## Purpose
`rpcattack.py` implements RPC-based relay attacks for Task Scheduler command execution (`TSCH`) and AD CS ICPR certificate enrollment (`ICPR`). It also provides the `RPCAttack` dispatcher used directly for RPC targets and indirectly by SMB relay when binding named pipes.

## Important APIs, Types, and Functions
- `ELEVATED` tracks usernames already used for ICPR certificate requests.
- `TSCHRPCAttack._xml_escape()` and `_run()` build/register/run/delete a scheduled task executing `config.command`.
- `ICPRRPCAttack._run()` builds a CSR and calls `icpr.hCertServerRequest()`, then writes a PFX.
- `RPCAttack(ProtocolAttack, TSCHRPCAttack)` registers `PLUGIN_NAMES = ["RPC"]`, stores DCE transport/stringbinding/endpoint, and dispatches by `config.rpc_mode`.

## Control Flow
For TSCH, `_run()` creates a random task name, builds a UTF-16 task XML running `cmd.exe /C <command>` as LocalSystem, registers it over DCERPC, runs it, polls `SchRpcGetLastRunInfo` until a nonzero runtime appears, deletes the task, and logs completion. For ICPR, `_run()` generates a key/CSR, chooses a template, requests a certificate over the ICPR RPC interface, handles common DCERPC errors, converts DER to a certificate, serializes a PFX, and writes it to `lootdir`.

## State and Persistence Behavior
TSCH mutates remote scheduled-task state temporarily and executes a command without output collection. ICPR creates CA request/certificate state and writes a local `.pfx`. `ELEVATED` is process-global and username-keyed.

## Dependencies and Integration Points
It depends on `OpenSSL.crypto`, `cryptography.x509`, Impacket DCERPC modules `tsch` and `icpr`, `NULL`, `DCERPCSessionError`, `ADCSAttack` helpers, and `ProtocolAttack`. `SMBAttack` can instantiate `RPCAttack` after binding to `\atsvc` or `\cert`.

## Risks and Edge Cases
- TSCH command output is not captured; success is inferred from last run info.
- Polling can wait indefinitely if last run info never updates.
- XML escaping covers core characters but command semantics remain operator-controlled.
- ICPR PFX is unencrypted, and the global `ELEVATED` cache is not target-specific.
- Certificate request behavior depends on template, CA name, and RPC encryption requirements.

## Test Signals
Unit tests should fake DCE calls for task XML creation, run polling, delete behavior, ICPR success/failure codes, PFX filename generation, and duplicate-user skipping. Integration tests require TSCH and ICPR-accessible Windows targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/rpcattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/smbattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/smbattack.py

## Purpose
`smbattack.py` implements the default SMB relay attack. It can start an interactive SMB shell, install an executable as a service, run RPC sub-attacks over SMB named pipes, add machine accounts through SAMR, execute a command and retrieve output, enumerate local admins after access denial, or dump local SAM hashes.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "SMBAttack"` advertises the plugin.
- `SMBAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["SMB"]`.
- `__init__()` wraps raw SMB/SMB3 objects in `SMBConnection`, configures optional RPC attack transport, interactive `TcpShell`, or `ServiceInstall`.
- `__answer()` accumulates remote command output.
- `run()` dispatches RPC attack, interactive shell, service install, add-computer, command execution, or SAM dump.

## Control Flow
If `config.rpc_attack` is set, construction binds to `\atsvc` for TSCH or `\cert` for ICPR and creates an `RPCAttack`; `run()` delegates to it. Interactive mode starts `MiniImpacketShell`. Service mode installs and uninstalls the configured executable. Add-computer mode uses `RemoteOperations.connectSamr()` and SAMR calls to create a workstation trust account and set its password/control flags. Default admin mode enables remote registry, optionally executes a command and retrieves `ADMIN$\Temp\__output`, or saves SAM and dumps/export hashes.

## State and Persistence Behavior
Remote state can include named-pipe RPC calls, service creation/removal, SAMR machine-account creation, remote command execution, temporary output files, remote registry service state, and SAM hive reads. Local state includes the SMB connection wrapper, output buffer, optional TCP shell, service installer, and exported SAM hash files named from the remote host.

## Dependencies and Integration Points
It depends on Impacket SMB/SMB3/SMBConnection, DCERPC `tsch`, `icpr`, `samr`, `SMBTransport`, `RPCAttack`, `TcpShell`, `serviceinstall`, `MiniImpacketShell`, `RemoteOperations`, `SAMHashes`, and `EnumLocalAdmins`. It is a core ntlmrelayx attack plugin.

## Risks and Edge Cases
- Remote registry/service manipulation is intrusive and may leave artifacts on failure.
- Command execution relies on private `RemoteOperations` methods and a fixed temp output path.
- Add-computer password setting uses SAMR password change with a blank old NT hash and may fail depending on policies.
- SMB1 flag manipulation is performed to avoid invalid parameter errors.
- Local admin enumeration is only attempted on access denied and when configured.
- Many branches catch broad exceptions and log strings without structured recovery.

## Test Signals
Unit tests should fake SMB dialects, RPC attack setup, service install flow, SAMR add-computer calls, command output retrieval/deletion, registry access denial local-admin enumeration, and SAM dump cleanup. Integration tests need Windows SMB targets with controlled admin/non-admin relay accounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/smbattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/winrmattack.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/winrmattack.py

## Purpose
`winrmattack.py` implements an interactive WinRM shell for relayed WinRMS sessions. It creates a remote WS-Man shell, sends commands through SOAP envelopes, receives base64 stdout streams, and cleans up the remote shell.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "WINRMAttack"` advertises the plugin.
- `WinRMShell(cmd.Cmd)` manages the local interactive command loop and remote WS-Man shell ID.
- `WinRMShell.onecmd()` sends command and receive SOAP messages.
- `WinRMShell.do_exit()` sends a WS-Man Delete request and closes the local TCP shell.
- `WINRMAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["WINRMS"]`, creates a `TcpShell`, and starts the shell in `run()`.

## Control Flow
`WINRMAttack.run()` listens on a local TCP shell, constructs `WinRMShell`, and enters `cmdloop()`. `WinRMShell.__init__` sends a Create request to `/wsman` and extracts `ShellId` with regex. Each command sends a Command request with the shell ID, extracts a `CommandId`, sends a Receive request, extracts stdout stream elements, base64-decodes them, and prints output. `do_exit()` deletes the remote shell and closes the TCP shell.

## State and Persistence Behavior
Local state includes TCP shell streams, prompt metadata, HTTP client, and the remote `shell_id`. Remote state is a WinRM shell and commands executed within it; `do_exit()` attempts cleanup. No local files are written.

## Dependencies and Integration Points
It depends on `cmd`, `sys`, `re`, `base64`, `impacket.LOG`, `ProtocolAttack`, and `TcpShell`. It assumes an HTTP client that can POST SOAP to `/wsman`.

## Risks and Edge Cases
- SOAP XML is assembled with f-strings and command text is not XML-escaped.
- Regex extraction of `ShellId`, `CommandId`, and streams is brittle and can throw when missing.
- Only stdout is decoded; stderr stream content is ignored.
- `onecmd("exit")` calls `do_exit()` but does not immediately return before building a command envelope.
- The plugin name is `WINRMS`, so plain `WINRM` targets may not map unless client code uses that name.

## Test Signals
Tests should fake HTTP responses for shell creation, command execution, receive output, missing IDs, base64 decode failures, exit cleanup, and command XML escaping expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/winrmattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/__init__.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/__init__.py

## Purpose
This module defines the base class and dynamic plugin loader for ntlmrelayx protocol clients. It discovers client modules, imports them, extracts their advertised client classes, and registers them in `PROTOCOL_CLIENTS` for relay target handling.

## Important APIs, Types, and Functions
- `PROTOCOL_CLIENTS` maps protocol names to client classes.
- Module globals `client_idx` and `lock` generate unique client IDs.
- `ProtocolClient` stores server config, target host/port, target URL/object, extended-security flag, active session, and arbitrary session data.
- Abstract methods include `initConnection()`, `killConnection()`, `sendNegotiate()`, `sendAuth()`, `sendStandardSecurityAuth()`, `getSession()`, `keepAlive()`, and `isAdmin()`.
- Default helpers include `getSessionData()`, `getStandardSecurityChallenge()`, and `setClientId()`.

## Control Flow
On import, the module scans files under `impacket.examples.ntlmrelayx.clients`, skips `__*` and non-Python files, imports each module, reads `PROTOCOL_CLIENT_CLASS` or `PROTOCOL_CLIENT_CLASSES`, and registers classes under their `PLUGIN_NAME`. Client construction resolves target port from `target.port` or a subclass-provided default.

## State and Persistence Behavior
Global registry state and monotonically increasing client IDs are process-local. Each client instance holds a protocol session and session data. `setClientId()` increments the global counter under a lock.

## Dependencies and Integration Points
It depends on `importlib.resources.files`, `os`, `sys`, `threading.Lock`, and `impacket.LOG`. It is used by ntlmrelayx relay orchestration to instantiate protocol-specific target clients.

## Risks and Edge Cases
- Import-time discovery can trigger side effects in all client modules.
- Malformed plugins are silently ignored except for debug logs.
- `target.hostname` and `target.port` are assumed to exist.
- The global client ID is not persistent across process restarts and is only unique in-process.

## Test Signals
Tests should verify registry population, single and multiple client class loading, target port override/default behavior, abstract method errors, session-data default behavior, standard-security challenge default, and thread-safe client ID increments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/__init__.py -->
