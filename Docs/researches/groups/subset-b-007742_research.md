# subset-b-007742 research

Grouped research for OpenAFS Windows KfW include headers. Each section preserves the source path and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kcmacerr.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kcmacerr.h

Purpose: Defines Macintosh Project Mandarin/KClient error constants and copied MacTCP/DNR network error constants used by legacy Kerberos client compatibility code.

Important APIs/types/functions: Declares `typedef signed short OSErr`; the anonymous enum starts Kerberos client errors at `cKrbCorruptedFile = -1024` and reserves `cKrbKerberosErrBlock = -20000`; `ipBadLapErr` through `outOfMemory` mirror MacTCP negative return codes.

Control flow: No executable logic. Consumers compare negative `OSErr` values returned from KClient-style APIs or translate them into user-facing messages.

State and persistence: No state. The only persistence contract is numeric stability of exported error values.

Dependencies and integration points: Integrates with KClient/KServer compatibility layers, MacTCP-compatible error handling, and any Windows KfW code that keeps Macintosh-era error numbers for cross-platform behavior.

Risks: The header has no include guard and defines common names such as `outOfMemory`, which can collide. `OSErr` is fixed to 16 bits while some consumers may store errors in `long`. The source contains legacy copyright text with non-ASCII bytes, so encoding-preserving edits matter.

Test signals: Compile consumers that include it more than once and alongside Windows/Kerberos headers; verify exact numeric values and sign extension when converted to wider error types; exercise translation of user-cancelled, configuration, TCP, and DNS failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kcmacerr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/com_err.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/com_err.h

Purpose: Provides a small Kerberos IV-era substitute for MIT `com_err`, exposing error formatting, table-name lookup, and hook registration.

Important APIs/types/functions: Defines `err_func` as `LPSTR (*)(int,long)`; declares `com_err`, `mbprintf`, `error_message`, `error_table_name`, `set_com_err_hook`, and `reset_com_err_hook`. Under `WIN16`, public symbols are exported functions plus global function pointers; under other builds they are direct functions.

Control flow: This header only declares the API. Runtime callers report an error through `com_err`, which may dispatch to a hook installed with `set_com_err_hook`; `error_message` maps numeric table codes to strings.

State and persistence: Hook state and error tables live in the linked com_err implementation. No file persistence, but hook changes are process-global.

Dependencies and integration points: Pulls in `stdarg.h`, Windows `LPSTR` conventions, and K4 generated error-table headers such as `kadm_err.h` and `krberr.h`. Load-function wrappers in this tree use the newer K5 com_err header, so callers must include the matching variant.

Risks: The substitute uses mutable global hooks and non-const `LPSTR` return types. `LPSTR` is conditionally defined only off Windows, so include order matters on Windows. WIN16 function-pointer indirection can crash if not initialized.

Test signals: Compile under `_WIN32`, non-Windows, and legacy WIN16 macro sets; verify hook install/reset behavior, varargs formatting, table-name lookup, and compatibility with generated K4 error table initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/com_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/conf-pc.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/conf-pc.h

Purpose: Supplies PC, Windows, DOS, and OS/2 platform configuration for legacy Kerberos IV headers.

Important APIs/types/functions: Normalizes `_WIN32` to `WIN32`, Windows macro families to `WINDOWS`, and OS/2 macros to `OS2`; selects `BITS16` or `BITS32`; declares little-endian `LSBFIRST`; aliases BSD functions (`index`, `bcopy`, `bzero`) to C runtime calls; defines `u_char`, `u_long`, `u_short`, `u_int`, optional `DWORD`, and PC calling convention macros; includes `windows.h` and `windowsx.h` for Windows.

Control flow: Pure preprocessor configuration. It is included by `conf.h` through `osconf.h` before K4 types and prototypes are compiled.

State and persistence: No runtime state. It fixes build-time ABI assumptions such as byte order, pointer model, `MAXPATHLEN`, and random seed sources.

Dependencies and integration points: Depends on C runtime functions, Windows SDK headers, OS/2 `utils.h`, and `time`/`process` in WIN16 mode. DES and K4 API headers rely on its `FAR`, `PASCAL`, and integer definitions.

Risks: Global BSD macro aliases can conflict with modern libraries. `RANDOM_KRB_INT32_*` uses `time()` and `getpid()` as weak random seeds. The `DWORD` fallback may mismatch Windows SDK typedefs if include order is wrong.

Test signals: Preprocessor tests for `_WIN32`, `WIN16`, `MSDOS`, and `OS2`; compile DES/KRB headers after it; verify `LSBFIRST`, `BITS32`, `FAR`, `PASCAL`, and `MAXPATHLEN` definitions match the intended Windows ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/conf-pc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/conf.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/conf.h

Purpose: Central Kerberos IV configuration wrapper for OS, CPU, compiler, and C-library compatibility.

Important APIs/types/functions: Includes `osconf.h`, optionally `names.h` for `SHORTNAMES`, compensates for non-ANSI compilers by defining `const`, `volatile`, and `signed`, defines generic `pointer`, and supplies `PROTOTYPE(p)` to support old-style versus ANSI declarations.

Control flow: Compile-time only. It chooses prototype syntax and validates that byte order (`MSBFIRST` or `LSBFIRST`) and word size (`BITS16` or `BITS32`) have been set by platform headers.

State and persistence: No runtime state. It persists platform assumptions into all downstream declarations.

Dependencies and integration points: Included by `des.h` and `krb.h`; `osconf.h` routes to `conf-pc.h` for Windows/OpenAFS builds.

Risks: Compatibility macros can hide compiler diagnostics by redefining language keywords on non-ANSI builds. The hard `#error` checks are valuable but can break unusual cross-compilation environments where byte order or bitness is not predeclared.

Test signals: Compile K4 headers on the target Windows toolchain and on any compatibility toolchain; verify `PROTOTYPE` expands correctly for function declarations and that exactly one byte-order and bitness path is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/conf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/des.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/des.h

Purpose: Declares the Kerberos IV DES block, key schedule, checksum, encryption, key-parity, and random-key interfaces used by legacy K4 and AFS token code.

Important APIs/types/functions: Defines `des_cblock[8]`, `des_key_schedule[16]`, `DES_KEY_SZ`, `DES_ENCRYPT`, `DES_DECRYPT`, and compatibility aliases such as `C_Block`, `Key_schedule`, `key_sched`, and `cbc_cksum`. Declares `quad_cksum`, `des_key_sched`, `des_ecb_encrypt`, `des_pcbc_encrypt`, `des_is_weak_key`, `des_fixup_key_parity`, `des_check_key_parity`, `des_new_random_key`, random generator seed/init functions, and `des_cbc_cksum`.

Control flow: Header-only declaration surface. Runtime users typically derive or obtain a `des_cblock`, call `des_key_sched`, then pass the schedule to CBC/PCBC/ECB or checksum routines.

State and persistence: The random generator APIs imply process-local PRNG state in the DES library. No persistence is declared here.

Dependencies and integration points: Includes `mit_copy.h` and `conf.h`; depends on K4 calling-convention macros and `KRB_INT32`. Used by `krb4/krb.h` and by AFS/Kerberos IV token compatibility.

Risks: DES is obsolete cryptography. Key schedule layout is ABI-sensitive and old `FAR` annotations matter for legacy builds. `des_cblock_print` depends on `stdout` but this header does not include `stdio.h`.

Test signals: ABI-size checks for `des_cblock` and `des_key_schedule`; tests for weak-key and parity handling; known-answer tests for DES CBC/PCBC/checksums; compile tests with and without `NCOMPAT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/des.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/kadm_err.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/kadm_err.h

Purpose: Generated Kerberos administration error table header for the older K4 com_err ABI.

Important APIs/types/functions: Defines `KADM_*` numeric constants from `KADM_RCSID` through `KADM_PW_MISMATCH`, with `ERROR_TABLE_BASE_kadm = -1783126272L`. Declares `initialize_kadm_error_table(HANDLE *)` on Windows or `initialize_kadm_error_table(struct et_list **)` elsewhere. Compatibility macros map `init_kadm_err_tbl()` and `kadm_err_base`.

Control flow: Callers initialize the table into `_et_list`, then pass returned error codes to `com_err`/`error_message`.

State and persistence: Error table registration mutates the process-global `_et_list`. No durable persistence.

Dependencies and integration points: Depends on the K4 com_err error-list model and Windows `HANDLE` when `WINDOWS` is defined. It is consumed by admin-client code and any K4/Kadmin compatibility path that reports password or database errors.

Risks: The header is generated but lacks include guards. It declares a global `_et_list`, so combining multiple generated K4 error headers can create ownership and linkage confusion. The Windows signature differs from newer MIT com_err headers.

Test signals: Compile together with `krb4/com_err.h`; verify one-time table initialization and message lookup for representative admin failures; assert constants remain stable for binary compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/kadm_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/krb.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/krb.h

Purpose: Main legacy Kerberos IV public header: constants, packet structures, credential/ticket-file types, error-code aliases, byte-swap macros, and K4 function prototypes.

Important APIs/types/functions: Defines principal sizing (`ANAME_SZ`, `REALM_SZ`, `MAX_K_NAME_SZ`), ticket text `KTEXT_ST`, `AUTH_DAT`, `CREDENTIALS`, `MSG_DAT`, ticket-file header access via `tkt_ptr()`, KDC and client error constants, sendauth option bits, and aliases from `krb_*` names to older implementation names. Prototypes include ticket-file functions (`tf_init`, `tf_get_cred`, `tf_save_cred`, `tf_close`), credential acquisition (`krb_get_pw_in_tkt`, `krb_in_tkt`, `krb_get_cred`), request construction (`krb_mk_req`), KDC transport (`send_to_kdc`), realm/host helpers, and lifetime conversion.

Control flow: Applications initialize or locate a ticket store, obtain initial credentials, retrieve service tickets, build AP requests, and validate replies using structures declared here. Ticket file operations use `TKT_FILE`/`TKT_ENV` and mutable process state behind `tkt_ptr()`.

State and persistence: K4 tickets persist in ticket files or Kerberos memory mode (`KM_TKFILE`, `KM_KRBMEM`). Globals include `krb_err_txt`; debug flags and ticket-file state live in the implementation.

Dependencies and integration points: Includes `<conf.h>` and `<des.h>`. Windows builds depend on `BOOL`, `PASCAL`, and `FAR`; OpenAFS token conversion paths rely on `CREDENTIALS`, DES keys, and K4 service-ticket calls.

Risks: Fixed-size buffers and string APIs are truncation-prone. Byte-swap macros mutate arguments and are unsafe for expressions. DES/K4 protocol use is legacy. Prototypes differ under `WINDOWS` versus other builds, so ABI mismatches are easy.

Test signals: Compile Windows and non-Windows declaration paths; exercise ticket-file lifecycle, principal parsing, realm lookup, lifetime conversion, KDC retry handling, and AP request creation with known K4 test vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/krb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/krberr.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/krberr.h

Purpose: Generated Kerberos IV error-table registration shim for the older K4 com_err mechanism.

Important APIs/types/functions: Declares `initialize_krb_error_func(err_func func, HANDLE *)` on Windows or `initialize_krb_error_func(err_func func, struct et_list **)` elsewhere. Defines `ERROR_TABLE_BASE_krb = 39525376L`, `init_krb_err_func(erf)`, `krb_err_base`, and external `_et_list`.

Control flow: K4 code registers an `err_func` that translates offsets into text, then com_err lookup uses the registered table/list state.

State and persistence: Mutates process-global error table list state. No persistent storage.

Dependencies and integration points: Requires `err_func` from `krb4/com_err.h` and Windows `HANDLE` when compiled for Windows. Used with `krb_err_txt` and K4 error reporting.

Risks: No include guard and a generic `_et_list` declaration can collide with other generated K4 error tables. It registers a function rather than a static `struct error_table`, unlike newer K5 headers.

Test signals: Verify `init_krb_err_func` installs the expected translator, that `ERROR_TABLE_BASE_krb` aligns with K4 error offsets, and that multiple generated tables can coexist in target link mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/krberr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/mit_copy.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/mit_copy.h

Purpose: Carries the MIT Kerberos IV copyright, export-control notice, warranty disclaimer, and permission text.

Important APIs/types/functions: No code declarations. It is included by `krb4/des.h` to keep license terms with DES/Kerberos IV API use.

Control flow: None.

State and persistence: None in runtime terms. The licensing notice is source-tree metadata that should persist with redistributed headers.

Dependencies and integration points: Integrated through legacy MIT Kerberos headers and relevant redistribution documentation.

Risks: Removing or altering the notice can violate redistribution expectations. The export-control language is historical but relevant to provenance reviews.

Test signals: Static packaging checks should ensure the notice remains included with K4 DES/Kerberos headers and survives generated SDK packaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/mit_copy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/osconf.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/osconf.h

Purpose: Selects the appropriate Kerberos IV platform configuration header based on CPU, OS, and compiler macros.

Important APIs/types/functions: Defines `PC` for IBM PC, DOS, OS/2, and `_WIN32`; includes one platform header from a cascade such as `conf-bsdtahoe.h`, `conf-bsdvax.h`, `conf-bsdsparc.h`, or `conf-pc.h`.

Control flow: Preprocessor routing only. For this OpenAFS Windows tree, `_WIN32` leads to `conf-pc.h`, which establishes `WINDOWS`, `BITS32`, and `LSBFIRST`.

State and persistence: No runtime state. It determines compile-time ABI and portability assumptions for all K4 code.

Dependencies and integration points: Included by `conf.h`; downstream K4 DES and Kerberos headers depend on the selected platform definitions.

Risks: The nested macro cascade is old and incomplete for modern platforms. If no platform branch matches, `conf.h` later fails with missing byte-order/bitness errors. A wrong branch can silently set incompatible integer or calling-convention assumptions.

Test signals: Preprocessor tests for `_WIN32` selecting `conf-pc.h`; negative tests for unsupported platform macros; compile DES/KRB headers after routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/osconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/des.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/des.h

Purpose: MIT Kerberos V distribution's Kerberos IV DES compatibility header, with newer ABI guards and Windows/Mac handling.

Important APIs/types/functions: Defines `DES_INT32`/`DES_UINT32`, `des_cblock`, a safer `des_key_schedule[16]`, DES constants and K4 compatibility aliases, and prototypes for `des_key_sched`, `des_pcbc_encrypt`, `des_quad_cksum`, `des_cbc_cksum`, `des_string_to_key`, `afs_string_to_key`, password reading, ECB/CBC encryption, parity, weak-key, random-key, and `des_cblock_print_file`.

Control flow: Consumers build a key schedule from an 8-byte key, then call encryption/checksum routines. The header suppresses public prototypes for internal crypto builds via `KRB5INT_CRYPTO_DES_INT`.

State and persistence: Declares random generator seed/init APIs with implementation-owned process state. No persistent data.

Dependencies and integration points: Includes `<win-mac.h>` on Windows and `stdio.h` for `FILE`. Used by `KerberosIV/krb.h` and K4 compatibility inside K5/OpenAFS code.

Risks: DES is obsolete. The header documents historical ABI changes, especially key schedule layout and return types, so mixing library/header versions can corrupt memory or link incorrectly. Mac packing pragmas affect structure layout.

Test signals: ABI-size checks, known-answer DES tests, random-key seed behavior, compile tests with `_WIN32`, `KRB4`, `NCOMPAT`, and `KRB5INT_CRYPTO_DES_INT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/des.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/kadm_err.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/kadm_err.h

Purpose: Newer generated K4 administration error table header using the K5 com_err `struct error_table` model.

Important APIs/types/functions: Includes `<com_err.h>`, defines the `KADM_*` constants from `KADM_RCSID` through newer values such as `KADM_NOT_SERV_PRINC` and `KADM_REALM_TOO_LONG`, sets `ERROR_TABLE_BASE_kadm`, and declares `extern const struct error_table et_kadm_error_table`. On non-Windows it declares `initialize_kadm_error_table`; on Windows initialization is a no-op macro.

Control flow: Error table lookup uses the static `et_kadm_error_table`; non-Windows callers can register it explicitly, while Windows builds rely on static or DLL-provided table availability.

State and persistence: Error table registration is process-global when used. No durable storage.

Dependencies and integration points: Uses `krb5/com_err.h` semantics and is consumed by KerberosIV compatibility/admin code.

Risks: This header differs from `krb4/kadm_err.h` in initialization signature and constant set. Including the wrong one can produce link errors or missing newer error constants.

Test signals: Verify constants and base values; compile with K5 `com_err.h`; assert `error_message(KADM_*)` works when table registration is expected; Windows tests should ensure the no-op initializer is compatible with the DLL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/kadm_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/krb.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/krb.h

Purpose: Kerberos V distribution's Kerberos IV compatibility API, exposing K4 structures and functions while integrating with K5 profile, com_err, and context types.

Important APIs/types/functions: Defines K4 principal/ticket sizing, `KTEXT_ST`, `AUTH_DAT`, `CREDENTIALS`, `MSG_DAT`, K4 error constants mapped through `KRBET_*`, sendauth options, profile section names for v4 realms, `key_proc_type`, `decrypt_tkt_type`, and globals such as `krb_ignore_ip_address`, `krb_debug`, and `krb5__krb4_context`. Prototypes cover ticket management (`dest_tkt`, `tkt_string`, `tf_*`), KDC/realm lookup, initial credential acquisition with password/preauth/creds, AP request/response generation and reading, service-key access, K5 conversion helpers, password change, profile access, default user, and Windows notification/time helpers.

Control flow: K4 compatibility callers acquire or locate ticket files, fetch TGTs/service tickets, build AP requests, validate server replies, and optionally bridge to K5 keyblocks/context. Realm and string-to-key behavior can be driven by K5 profile sections.

State and persistence: Ticket files persist through `TKT_FILE` or caller-set ticket strings; profile-backed realm settings are read through `profile.h`; globals hold debug, address-ignore, and K4-over-K5 context state.

Dependencies and integration points: Includes `<kerberosIV/des.h>`, `<kerberosIV/krb_err.h>`, and `<profile.h>`, with Windows additions from `<time.h>` and `win-mac.h` transitively. OpenAFS uses these declarations when KfW-backed Kerberos IV/AFS token compatibility is needed.

Risks: K4 and DES are legacy. This header intentionally exposes many private functions except on some Mac builds. ABI varies by `_WIN32`, Mac packing, and `KRB_PRIVATE`. Mixing it with older `krb4/krb.h` can cause conflicting prototypes and error-code semantics.

Test signals: Compile K4 compatibility users against this exact header; test profile-driven realm lookup, ticket-file set/get, KDC retry failures, AP request validation, K5 key conversion, password-change path, and Windows notification/time helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/krb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/krb_err.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/krb_err.h

Purpose: Generated Kerberos IV error table for the K5 com_err model.

Important APIs/types/functions: Includes `<com_err.h>`, defines `KRBET_*` constants from `KRBET_KSUCCESS` through reserved slots and named K4 failures, sets `ERROR_TABLE_BASE_krb = 39525376L`, and declares `extern const struct error_table et_krb_error_table`. Non-Windows builds also declare `initialize_krb_error_table`.

Control flow: `KerberosIV/krb.h` maps legacy small K4 error numbers with `KRB_ET(x)`, while com_err users can look up full table codes through `et_krb_error_table`.

State and persistence: Optional table registration mutates process-global com_err state. No durable state.

Dependencies and integration points: Must be paired with K5 `com_err.h` and `KerberosIV/krb.h`. It is not ABI-equivalent to `krb4/krberr.h`.

Risks: Very large generated macro surface increases collision risk. Windows no-op initialization assumes the table is already linked into the library. Using `KRBET_*` full codes where legacy offset codes are expected changes behavior.

Test signals: Verify `KRB_ET` mappings in `KerberosIV/krb.h`, message lookup for representative failures (`KDC`, `GC`, `RD_AP`, ticket-file errors), and compile/link behavior on Windows where initializers are macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/krb_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/mit-copyright.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/mit-copyright.h

Purpose: MIT KerberosIV copyright, export-control notice, modified-software labeling requirement, and warranty disclaimer.

Important APIs/types/functions: No executable declarations.

Control flow: None.

State and persistence: No runtime state. The notice is retained as source distribution metadata for KerberosIV compatibility headers.

Dependencies and integration points: Applies to redistributed KerberosIV files in the K5 include subtree and should be preserved by SDK packaging.

Risks: Removing or changing the notice can create licensing/provenance issues. The modified-software clause is stricter than a bare permissive notice and should be visible to downstream packagers.

Test signals: Packaging and license-audit checks should ensure this file is included with KerberosIV headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/mit-copyright.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/com_err.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/com_err.h

Purpose: Public MIT common-error library header used by Kerberos 5 and generated error tables.

Important APIs/types/functions: Defines `errcode_t`, `et_old_error_hook_func`, `struct error_table`, and public APIs `com_err`, `com_err_va`, `error_message`, `add_error_table`, and `remove_error_table`. Non-Windows builds also expose `set_com_err_hook` and `reset_com_err_hook`.

Control flow: Libraries register generated `struct error_table` instances, callers format/report errors through `com_err` or retrieve text with `error_message`, and registered tables can be removed.

State and persistence: Error table registry and optional hooks are process-global implementation state. No file persistence.

Dependencies and integration points: Includes `win-mac.h` on Windows for calling conventions and `stdarg.h` for varargs. Used by K5 core errors, profile errors, Kadmin errors, KerberosIV generated errors, and `loadfuncs-com_err.h`.

Risks: Windows intentionally hides global hook APIs to avoid cross-application display hooks. Returned strings are observer/dependent memory and must not be freed by callers. Calling convention macros must match the loaded DLL.

Test signals: Register/remove table tests, `error_message` fallback tests, varargs formatting through `com_err_va`, and dynamic-load tests that confirm `KRB5_CALLCONV`/`KRB5_CALLCONV_C` signatures match `comerr32.dll` or `comerr64.dll`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/com_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi.h

Purpose: GSS-API C binding declarations used by Kerberos mechanisms for credential acquisition, security context establishment, MIC/wrap operations, name/OID management, and status reporting.

Important APIs/types/functions: Defines opaque `gss_name_t`, `gss_cred_id_t`, `gss_ctx_id_t`, `OM_uint32`, OID/buffer/channel-binding structs, context flag bits, credential usage constants, major status bit fields, `GSS_ERROR`, and static OID variables such as `GSS_C_NT_USER_NAME` and `GSS_C_NT_HOSTBASED_SERVICE`. Prototypes include `gss_acquire_cred`, `gss_init_sec_context`, `gss_accept_sec_context`, `gss_get_mic`, `gss_verify_mic`, `gss_wrap`, `gss_unwrap`, status/display/name import/release functions, OID-set helpers, context export/import, and V1 compatibility names `gss_sign`, `gss_seal`, `gss_unseal`.

Control flow: Initiators import a target name, acquire credentials, loop `gss_init_sec_context` tokens with an acceptor running `gss_accept_sec_context`, then protect messages with MIC/wrap APIs until context deletion.

State and persistence: Opaque credentials, names, contexts, buffers, and OID sets are implementation-owned handles. Callers must release returned buffers, names, credentials, OID sets, and contexts with matching GSS APIs. Exported contexts can be serialized for interprocess transfer.

Dependencies and integration points: Uses Kerberos calling-convention macros and Windows DLL import/export decoration. Integrated by `gssapi_generic.h`, `gssapi_krb5.h`, Kerberos-aware clients, and OpenAFS authentication glue.

Risks: Ownership rules are strict and easy to leak. Major status combines calling, routine, and supplementary bits, so tests must use masks. The header exposes deprecated OIDs and V1 entrypoints for compatibility. Channel-binding/address constants must match peer expectations.

Test signals: GSS init/accept loop, name import/export/canonicalization, wrap/MIC round trips, major/minor status display, context export/import, OID-set creation/release, and Windows DLL import linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi_generic.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi_generic.h

Purpose: Compatibility header exporting deprecated MIT generic GSS name-type OID variables.

Important APIs/types/functions: Includes `<gssapi/gssapi.h>` and declares `gss_nt_user_name`, `gss_nt_machine_uid_name`, `gss_nt_string_uid_name`, `gss_nt_service_name_v2`, `gss_nt_service_name`, and `gss_nt_exported_name`.

Control flow: No runtime logic. Consumers pass these OID variables to GSS name import/compare/display APIs.

State and persistence: OID variables refer to implementation-owned static storage. Callers must not free them.

Dependencies and integration points: Bridges old MIT names to RFC 2744 OID constants in `gssapi.h`. Used by older applications that have not migrated to `GSS_C_NT_*`.

Risks: Deprecated aliases can obscure which OID should be emitted. Some declarations lack `GSS_DLLIMP`, so Windows import/export behavior may differ across symbols.

Test signals: Compile legacy users, verify each alias points to the expected OID, and run name import tests using both deprecated and RFC names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi_krb5.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi_krb5.h

Purpose: Kerberos-specific GSS-API extension header for mechanism OIDs, Kerberos name OIDs, credential/cache helpers, enctype restrictions, and lucid context export.

Important APIs/types/functions: Declares Kerberos mechanism OIDs (`gss_mech_krb5`, old/wrong variants, mechanism sets), Kerberos name OIDs, `gss_uint64`, lucid key/context structs (`gss_krb5_lucid_key_t`, RFC1964 and CFX keydata, `gss_krb5_lucid_context_v1_t`), and APIs `krb5_gss_register_acceptor_identity`, `gss_krb5_get_tkt_flags`, `gss_krb5_copy_ccache`, `gss_krb5_ccache_name`, `gss_krb5_set_allowable_enctypes`, `gss_krb5_export_lucid_sec_context`, and freeing helpers.

Control flow: Applications can set acceptor identity, acquire/copy Kerberos credentials into a ccache, restrict negotiated enctypes before `gss_init_sec_context`, and export an established context into readable key/sequence fields for protocol integrations.

State and persistence: Ccache name changes and acceptor identity are process/global library state. Exported lucid context memory is caller-owned until freed through the matching GSS extension. Ccache operations may persist credentials in the selected Kerberos cache.

Dependencies and integration points: Includes `gssapi.h` and `krb5.h`; tightly integrates GSS with Kerberos credential caches, key enctypes, and OpenAFS/Kerberos token workflows.

Risks: Lucid context export invalidates or consumes the original context handle as documented. Exported keys are sensitive material and must be freed promptly. Old/wrong OIDs exist for compatibility and can cause negotiation surprises.

Test signals: Register acceptor identity, copy credentials to a ccache, set allowable enctypes before context creation, inspect ticket flags, export/free lucid contexts for both RFC1964 and CFX protocols, and verify sensitive buffers are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi_krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/krb5.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/krb5.h

Purpose: Backward-compatible forwarding header for software that still includes `<krb5.h>` from the old install location.

Important APIs/types/functions: Contains only a comment explaining the header move and `#include <krb5/krb5.h>`.

Control flow: Preprocessor forwarding only.

State and persistence: None.

Dependencies and integration points: Depends on include paths resolving `krb5/krb5.h` to the real MIT Kerberos public header. It preserves source compatibility for older OpenAFS/KfW consumers.

Risks: Include-path ordering can accidentally pick another `krb5/krb5.h`. Because this file has no guard of its own, it relies on the real header's guard.

Test signals: Compile legacy `#include <krb5.h>` consumers and verify they receive the same declarations as direct `#include <krb5/krb5.h>` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/krb5/krb5.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/krb5/krb5.h

Purpose: Main MIT Kerberos 5 public API header vendored for Windows KfW: core scalar types, protocol structures, crypto/checksum APIs, credential-cache/keytab APIs, authentication APIs, configuration helpers, and generated error constants.

Important APIs/types/functions: Defines Kerberos scalar types (`krb5_context`, `krb5_principal`, `krb5_data`, `krb5_keyblock`, `krb5_creds`, tickets, authenticators, KDC requests/replies, auth context, ccache/keytab handles), encryption and checksum constants, protocol flags, preauth/authdata/message type constants, and many APIs. Major groups include crypto (`krb5_c_encrypt`, `krb5_c_decrypt`, random, checksum, string-to-key), credential caches (`krb5_cc_*`), keytabs (`krb5_kt_*`), contexts (`krb5_init_context`, `krb5_free_context`), credential acquisition (`krb5_get_init_creds_password/keytab`, `krb5_get_credentials`), AP/safe/private messages (`krb5_mk_req`, `krb5_rd_req`, `krb5_mk_safe`, `krb5_rd_priv`), principal parsing/copy/free helpers, auth-context setters, password change, realm/profile/config helpers, time helpers, and generated KRB5/KDB/KV5M error tables.

Control flow: A typical caller initializes a `krb5_context`, parses principals, opens or creates a credential cache/keytab, obtains or retrieves credentials, builds or validates protocol messages through auth contexts, and then frees every object through the corresponding `krb5_free_*` or close API. Error messages flow through com_err tables and optional per-context extended error strings.

State and persistence: Contexts own configuration/profile state; credential caches and keytabs can persist tickets/keys on disk or OS cache backends; replay caches and auth contexts hold sequence/time/subkey state; default realms, config files, and ccache names are process or profile mediated.

Dependencies and integration points: Includes Windows/Mac ABI support, com_err tables, profile integration, and optional K4 conversion declarations. GSS/Kerberos extensions include this header, and OpenAFS Windows authentication code depends on its ccache, keytab, enctype, and principal APIs.

Risks: Huge ABI surface with historical `KRB5_CALLCONV_WRONG` exports means calling convention must match binaries. Many returned allocations require exact free functions. Deprecated DES/old crypto APIs coexist with newer APIs. Generated error constants are stable API and should not be renumbered.

Test signals: Compile and link against target KfW DLLs; run context init/free, default realm/profile loading, password/keytab initial creds, ccache store/retrieve/iterate, keytab read/iterate, AP request validation, GSS integration, error-message lookup, and leak checks for all copy/free pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/krb5/krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/profile.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/profile.h

Purpose: MIT Kerberos profile/configuration API plus generated profile error constants.

Important APIs/types/functions: Defines opaque `profile_t`, file-spec typedefs, iterator flags, and APIs for initialization (`profile_init`, `profile_init_path`), flushing (`profile_flush`, `profile_flush_to_file`, `profile_flush_to_buffer`), writability/modified checks, abandon/release, value retrieval, list freeing, integer/boolean parsing, relation/subsection names, iterator creation/use/free, string release, relation update/clear/add, and section rename. Appended generated errors include `PROF_*` constants and `et_prof_error_table`.

Control flow: Kerberos code opens one or more profile files, reads named section/relation paths, optionally mutates relations or sections, flushes changes, then releases the profile handle. Iterators enumerate matching relations or sections.

State and persistence: Profile handles retain parsed configuration and dirty state. `profile_flush*` writes to disk or buffer; `profile_abandon` discards changes; `profile_release` frees handles. Returned strings/lists must be released with profile APIs.

Dependencies and integration points: Includes `win-mac.h` and `com_err.h`. Consumed by `krb5.h`, `KerberosIV/krb.h`, realm mapping, app defaults, and KfW configuration tools.

Risks: Mutation APIs can persist configuration changes. Returned buffers require correct freeing. The header appends generated error-table definitions after the include guard, so repeated includes may still expose those macros/declarations.

Test signals: Init from file list/path, get string/integer/boolean defaults and bad values, iterate sections/relations, update/rename/clear/add then flush to buffer/file, abandon dirty profiles, and verify profile error messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/profile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/win-mac.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/win-mac.h

Purpose: Windows platform ABI support header for MIT Kerberos/KfW public headers.

Important APIs/types/functions: Defines read-password dialog IDs, enforces 32-bit `time_t` compatibility on 32-bit MSVC builds when included from internal Kerberos headers, sets `SIZEOF_*`, includes `windows.h`, defines `SIZE_MAX`, declares `KRB5_CALLCONV`, `KRB5_CALLCONV_C`, and `KRB5_CALLCONV_WRONG`, supplies system typedefs such as `u_long`, `u_int`, `u_short`, and compatibility macros such as `THREEPARAMOPEN`.

Control flow: Preprocessor-only setup used before public function prototypes are emitted. Some branches are resource-compiler-only via `RES_ONLY`.

State and persistence: No runtime state. It locks ABI assumptions for time, integer sizes, and calling conventions.

Dependencies and integration points: Included by `krb5.h`, `com_err.h`, `profile.h`, and KerberosIV DES headers on Windows. It binds public declarations to KfW DLL export conventions.

Risks: Include order matters: if `time_t` has already been defined as 64-bit in 32-bit Windows builds, the header deliberately errors to prevent ABI mismatch. Global Windows includes and typedefs can collide with other portability layers.

Test signals: Compile with MSVC 32-bit and 64-bit settings, resource compiler mode, and public-header-only mode; verify calling conventions in generated import libraries and that `time_t` ABI checks fire when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/win-mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krbcc/cacheapi.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krbcc/cacheapi.h

Purpose: Public Kerberos Common Cache DLL API for managing named credential caches containing Kerberos V and legacy Kerberos IV credentials.

Important APIs/types/functions: Defines `cc_int32`, `cc_uint32`, `cc_time_t`, API versions, `CCACHE_API`, error codes, opaque handles `apiCB`, `ccache_p`, `ccache_cit`, `cc_data`, V5 `cc_creds`, V4 `V4Cred_type`, `cred_union`, `infoNC`, cache version constants, and lock constants. APIs include `cc_initialize`, `cc_shutdown`, `cc_get_change_time`, named-cache create/open/close/destroy/iterate/info/principal/version/lock, credential store/remove/iterate, and DLL-owned free functions.

Control flow: Clients initialize an API control block, open or create named caches, set principals, store or fetch V4/V5 credentials through iterators, optionally lock caches, free returned allocations with cache API free calls, then shut down.

State and persistence: The DLL owns main cache state and named caches; credential data can persist in the common cache backend. `cc_get_change_time` reports global mutation time. Handles and iterators are opaque DLL state.

Dependencies and integration points: Includes `windows.h`, exports via `__declspec(dllexport)`, and bridges KfW credential cache operations used by Kerberos and OpenAFS token acquisition.

Risks: The header always defines `CCACHE_API` as export, which is awkward for import-side consumers unless build flags compensate. Cross-DLL allocation ownership is strict. V4 fixed buffers and V5 pointer graphs require deep-copy/free correctness. Lock semantics are cooperative and easy to misuse.

Test signals: Initialize/shutdown version negotiation, create/open/destroy caches, store/fetch V4 and V5 credentials, iterator begin/next/end edge cases, lock/no-block behavior, change-time updates, and correct nulling/freeing of returned pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/krbcc/cacheapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leasherr.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leasherr.h

Purpose: Generated error table for Leash, the Windows Kerberos credential UI/helper layer.

Important APIs/types/functions: Defines `LSH_*` errors covering singleton enforcement, invalid principal/instance/realm, EOF, expiry, bad characters, Winsock/time-server/socket/connect failures, time receive/set failures, and `LSH_ALREADY_SETTIME`. Declares `initialize_lsh_error_table(struct et_list **)`, sets `ERROR_TABLE_BASE_lsh`, and compatibility macros `init_lsh_err_tbl()` and `lsh_err_base`.

Control flow: Leash code initializes the table and reports these codes through com_err-style lookup.

State and persistence: Error-table initialization mutates process-global `_et_list`. No durable state.

Dependencies and integration points: Depends on old com_err `struct et_list` and is used by Leash UI/API calls in `leashwin.h`.

Risks: No include guard and reliance on `_et_list` can collide with other old generated tables. The declarations match older com_err, not the newer K5 `struct error_table` model.

Test signals: Compile with the intended com_err header, initialize the table, look up representative Leash errors, and verify values remain stable for external callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leasherr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leashinfo.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leashinfo.h

Purpose: Defines resource/configuration identifiers used by Leash for time-host and default ticket-life settings.

Important APIs/types/functions: Defines `LSH_TIME_HOST = 1970` and `LSH_DEFAULT_TICKET_LIFE = 1971`.

Control flow: No executable logic. Consumers use these numeric IDs to load or store Leash settings/resources.

State and persistence: No state in the header. The IDs point to settings that are likely persisted by Leash configuration code elsewhere.

Dependencies and integration points: Integrated with Leash resource and configuration handling.

Risks: No include guard and very generic numeric constants can collide if included in broad resource contexts. Changing values breaks compatibility with existing resources/configuration.

Test signals: Resource compile tests and Leash configuration tests that read/write time-host and default lifetime by these IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leashinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leashwin.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leashwin.h

Purpose: Public Windows Leash API for Kerberos login/password dialogs, ticket operations, ticket status display, and user-default configuration.

Important APIs/types/functions: Includes `<krb.h>`, defines dialog type constants, `LSH_DLGINFO`, versioned `LSH_DLGINFO_EX`, optional wide-character `NETID_DLGINFO`, `TICKETINFO`, ticket state constants, and function prototypes for kinit/change-password dialogs, password check/change, `Leash_kinit*`, `Leash_klist`, `Leash_kdestroy`, error retrieval, renew/import, help-file access, default reset, and many registry-backed default getters/setters/resets for lifetime, renewability, forwardable, addresses, proxiable, public IP, KRB4 use, option hiding, lock file locations, uppercase realm, MSLSA import, and preserving settings.

Control flow: UI callers populate dialog info structs, invoke modal Leash dialogs or direct kinit/change-password functions, list/destroy/renew/import tickets, and adjust defaults through registry-oriented setters.

State and persistence: Ticket operations mutate Kerberos credential caches. Default setters alter current-user registry configuration. Dialog structs carry both input and output fields with explicit size-version macros for ABI negotiation.

Dependencies and integration points: Depends on Windows types, K4/Kerberos declarations from `<krb.h>`, NetIDMgr-compatible wide structs when not building NetIDMgr, and Leash DLL exports.

Risks: Struct versioning is size-based and sensitive to packing/pointer width. ANSI `LPSTR` fields coexist with fixed internal buffers. Registry mutations and ticket destruction are user-visible. K4 include path choice affects `MAX_K_NAME_SZ`.

Test signals: Dialog ABI tests for V1/V2/V3 sizes, kinit/change-password success and cancellation, klist states for no/expired/good tickets, registry default round trips, help file set/get, and 32/64-bit struct layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leashwin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-afs.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-afs.h

Purpose: Dynamic-load function typedef list for modern OpenAFS token/configuration DLLs used by KfW integration.

Important APIs/types/functions: Defines `AFSTOKENS_DLL` as `libafstokens.dll`, `AFSCONF_DLL` as `libafsconf.dll`, `cm_configProc_t`, and `TYPEDEF_FUNC` entries for `ktc_ListTokens`, `ktc_GetToken`, `ktc_SetToken`, `ktc_ForgetAllTokens`, `cm_SearchCellFile`, and `cm_GetRootCellName`.

Control flow: Included by the generic load-functions framework, which expands `TYPEDEF_FUNC` into function-pointer typedefs, globals, or loader entries. Runtime code loads the DLLs and calls resolved AFS token/cell functions.

State and persistence: This header has no state. Resolved function pointers and loaded module handles are held by the loadfuncs implementation. Token calls mutate AFS token state; cell functions read AFS cell configuration.

Dependencies and integration points: Depends on `loadfuncs.h`, `struct ktc_principal`, `struct ktc_token`, and `struct sockaddr_in` declarations from AFS/network headers. Used by OpenAFS Windows Kerberos-to-AFS token paths.

Risks: Function signatures must match the target DLL exactly. This modern variant has `ktc_SetToken(server, client, token, flags)` and `cm_SearchCellFile(cell, proc, rock)` signatures that differ from the AFS 3.6 header.

Test signals: Dynamic-load tests for DLL names and all exports; call-signature smoke tests for list/get/set/forget tokens; root-cell and cell-file search tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-afs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-afs36.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-afs36.h

Purpose: Dynamic-load function typedef list for older AFS 3.6-style token/configuration DLLs.

Important APIs/types/functions: Defines `AFSTOKENS_DLL` as `afsauthent.dll`, `AFSCONF_DLL` as `libafsconf.dll`, the same `cm_configProc_t`, and `TYPEDEF_FUNC` entries for token and cell functions. Signatures differ from the modern header: `ktc_SetToken(struct ktc_principal *, struct ktc_token *, struct ktc_principal *, int)` and `cm_SearchCellFile(char *, char *, cm_configProc_t *, void *)`.

Control flow: The loadfuncs framework resolves old DLL exports and lets compatibility code call AFS 3.6 entrypoints through the generated pointers.

State and persistence: No state in the header. Runtime loader state is external; token APIs mutate AFS authentication state and cell search reads configuration.

Dependencies and integration points: Depends on `loadfuncs.h`, AFS token structs, and socket address declarations. It exists specifically to support older AFS client deployments.

Risks: The header guard closing comment names the modern guard, a minor maintenance hazard. Accidentally using modern call order with old function pointers can corrupt arguments. DLL name selection changes deployment requirements.

Test signals: Load `afsauthent.dll`, verify old export signatures, exercise token set/get/list/forget, and test old four-argument `cm_SearchCellFile` behavior separately from the modern path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-afs36.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-com_err.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-com_err.h

Purpose: Dynamic-load function typedef list for the KfW com_err DLL.

Important APIs/types/functions: Includes `loadfuncs.h` and `<com_err.h>`, selects `COMERR_DLL` as `comerr64.dll` on `_WIN64` or `comerr32.dll` otherwise, and declares `TYPEDEF_FUNC` entries for `com_err`, `com_err_va`, `error_message`, `add_error_table`, and `remove_error_table` using K5 calling conventions.

Control flow: The loadfuncs framework resolves com_err exports at runtime, allowing OpenAFS/KfW glue to format errors and register/unregister error tables without static linking.

State and persistence: Header has no state. Loaded function pointers/module handles live in loadfuncs code; the com_err DLL owns process-global error table registry state.

Dependencies and integration points: Depends on K5 `com_err.h` types and `KRB5_CALLCONV` macros. Integrates generated Kerberos/profile/Leash error tables with dynamically loaded KfW com_err.

Risks: DLL bitness must match process bitness. Varargs function pointer calls must use the exact calling convention. Including the old K4 `com_err.h` instead of K5 would produce incompatible prototypes.

Test signals: Dynamic-load both bitness-specific DLL names in matching environments; resolve all exports; register a generated error table and verify `error_message`; exercise `com_err_va` with varargs forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-com_err.h -->
