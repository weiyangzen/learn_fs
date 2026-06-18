# Research: subset-b-007837

Grouped research for OrangeFS client webpack S3 module, webpack helper scripts, Windows wxWidgets GUI files, and Windows client-service credential/config/Dokan files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/webpack/d.s3/mod_orangefs_s3.c -->
# sources/distributed-fs/orangefs/src/client/webpack/d.s3/mod_orangefs_s3.c

## Purpose
This file implements an Apache httpd content/authentication module that exposes an Amazon S3-like REST surface over an OrangeFS/PVFS2 namespace. It maps buckets to directories under a configured `BucketRoot`, maps objects to PVFS files, stores S3 metadata in PVFS extended attributes, and authenticates requests using an Apache `AuthType AWS` hook with configured access keys.

## Important APIs, types, and functions
- Apache module entry points: `orangefs_s3_module`, `orangefs_s3_cmds`, `orangefs_s3_register_hooks`, `orangefs_s3_handler`, `orangefs_s3_authenticate_aws_user`, `orangefs_s3_post_config`.
- Server configuration: `orangefs_s3_config` holds `bucket_root`, `PVFSInit`, root owner/display values, resolved `pvfs_path`, `awsAccounts`, resolved `fsid`, and a `quit` flag used by recursive listing.
- Request context: `orangefs_s3_request` wraps the Apache `request_rec`, config, APR pool, parsed query params, user/root PVFS credentials, and authenticated name fields.
- S3 account config: `orangefs_s3_aws_account` stores access id, secret key, uid, and gid configured by `AWSAccount`.
- PVFS-backed object operations: `orangefs_s3_put_object`, `orangefs_s3_get_object`, `orangefs_s3_delete_object`, `orangefs_s3_copy_object` (stub).
- Bucket/service operations: `orangefs_s3_put_bucket`, `orangefs_s3_get_bucket`, `orangefs_s3_delete_bucket`, `orangefs_s3_get_service`, and placeholder subresource handlers for ACL/lifecycle/policy/location/logging/notification/versioning/website.
- Helpers: `orangefs_s3_load_post_data`, `parse_form_from_string`, `orangefs_s3_recurse`, `orangefs_s3_write_post_data_ref`, `orangefs_s3_authorized`, `orangefs_s3_mkdir_p`, `orangefs_s3_get_signature_data`, `orangefs_s3_get_aws_auth`.

## Control flow
Apache calls `orangefs_s3_authenticate_aws_user` during check-user-id. It accepts only `AuthType AWS`, parses `Authorization: AWS access_id:base64_signature`, looks up the configured account, builds a StringToSign, computes an HMAC-SHA1 with the configured secret key, and exports `AUTHENTICATE_CN`, `AUTHENTICATE_UIDNUMBER`, and `AUTHENTICATE_GIDNUMBER` into the request environment.

The content handler accepts only handler name `orangefs_s3`, reads those environment values, builds PVFS credentials plus a root credential, parses query parameters, and calls `orangefs_s3`. `orangefs_s3` resolves `BucketRoot` to an fs id and PVFS path for every request, then routes by host style and URI style: service request `/`, bucket request, or object request. Object `GET`, `PUT`, and `DELETE` call PVFS lookup/read/write/remove helpers. Bucket `GET`, `PUT`, and `DELETE` list, create, and remove PVFS directories.

Bucket listing uses `PVFS_sys_lookup` on the bucket directory, emits S3 XML, then recursively walks with `orangefs_s3_recurse`; `orangefs_s3_get_bucket_recurse` emits only non-directory entries as `<Contents>`. Service listing reads one batch of up to 60 entries under the bucket root and filters entries through `orangefs_s3_authorized`.

## State and persistence behavior
Persistent state lives in OrangeFS objects and extended attributes. Bucket and object owners are stored in `user.s3.owner.id` and `user.s3.owner.display-name`; object ETag and size are stored in `user.s3.entity-tag` and `user.s3.size`. PUT object writes request body bytes to the PVFS file, computes MD5, sets ETag/size/owner xattrs, and returns the ETag response header. GET object reads size and ETag xattrs if present, then streams PVFS file contents unless the HTTP method is `HEAD`.

Runtime state is per-request APR pool allocation plus server config. `awsAccounts` persists in the Apache server config pool. PVFS initialization is controlled by the `PVFSInit` directive so only one OrangeFS module initializes PVFS defaults when multiple modules are loaded.

## Dependencies and integration points
The file integrates Apache httpd/APR hooks and tables, PVFS2 sysint APIs, OpenSSL HMAC/EVP, libxml initialization, Unix passwd lookup, and S3-compatible HTTP clients. It expects upstream Apache authentication configuration to set `AuthType AWS` and the module handler to be bound to requests. `prepare.sh`/`pvfsinit.sh` in the same webpack area support module build and httpd `PVFSInit` coordination.

## Risks and edge cases
- AWS signature canonicalization is incomplete: `x-amz-*` headers are not lowercased, sorted, unfolded, or duplicate-collapsed, and canonical subresources are not appended. Interoperability with real S3 clients is fragile.
- `orangefs_s3_get_aws_auth` base64-decodes the signature and compares raw HMAC bytes, while classic S3 Authorization carries a base64 HMAC string after the colon. Any mismatch in expected encoding can reject valid clients.
- `apr_table_elts` is iterated as if header entries are triples (`headers->nelts*3` and `const char **`), but APR table entries are `apr_table_entry_t`; this can read invalid memory.
- `orangefs_s3_authorized` checks only owner id and has an empty ACL branch, so configured S3 ACL constants are not enforced.
- `parse_form_from_string` mutates `r->args` directly, which may surprise later Apache consumers.
- Request body loading/writing repeatedly reallocates APR buffers and lacks content-length limits. Large PUTs can consume memory or stream inefficiently.
- `orangefs_s3_mkdir_p` can recurse with `parent_path == NULL` for malformed relative paths and uses decimal literals for POSIX modes.
- XML responses interpolate unescaped bucket/object/metadata strings, so object names or display names containing XML-sensitive characters can produce invalid or unsafe XML.
- Object overwrite writes from offset 0 but does not visibly truncate existing larger files.
- Some PVFS request objects are freed only after loops; error paths may leak PVFS request handles or hints.
- Many S3 features are stubs returning `OK`, empty XML, or fixed errors; copy object is a no-op returning success.

## Test signals
Useful tests include Apache module load with multiple OrangeFS modules and `PVFSInit`, valid/invalid AWS signatures, path-style and virtual-host-style bucket routing, PUT/GET/HEAD/DELETE object round trips, overwrite with shorter object, bucket create/list/delete, non-owner service listing filtering, object names requiring XML escaping, large streaming PUT/GET, and real S3 client compatibility for canonicalized `x-amz-*` headers and subresources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/webpack/d.s3/mod_orangefs_s3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/webpack/prepare.sh -->
# sources/distributed-fs/orangefs/src/client/webpack/prepare.sh

## Purpose
This is a tiny bootstrap script for the webpack Apache module build area. It runs GNU libtool/autotools setup so generated build files are available before configure/build.

## Important APIs, types, and functions
The script invokes `libtoolize` and, only if that succeeds, `autoreconf -i`. There are no functions or arguments.

## Control flow
The shell executes `libtoolize && autoreconf -i`; failure of `libtoolize` prevents `autoreconf` from running and the script exits with the failing command status.

## State and persistence behavior
The script modifies the working tree by generating or updating autotools artifacts such as `aclocal.m4`, `configure`, `Makefile.in`, `config.guess`, or libtool helper files, depending on the surrounding autotools metadata.

## Dependencies and integration points
It depends on `/bin/sh`, GNU libtool, autoconf, automake/aclocal, and the local autotools input files. It is likely used before packaging or compiling the Apache modules under `src/client/webpack`.

## Risks and edge cases
No `set -e` is needed because the only sequence uses `&&`, but additional future lines would not inherit that behavior. The script has no portability checks for non-GNU libtool names such as `glibtoolize` on macOS and no version checks for autotools compatibility.

## Test signals
Run from the webpack directory in a clean checkout and verify `libtoolize` and `autoreconf -i` complete without missing macro errors. Re-run to confirm idempotence and no unexpected source churn beyond generated files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/webpack/prepare.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/webpack/pvfsinit.sh -->
# sources/distributed-fs/orangefs/src/client/webpack/pvfsinit.sh

## Purpose
This helper rewrites Apache `httpd.conf` so exactly one loaded OrangeFS Apache module receives a `PVFSInit` directive. It chooses the first loaded OrangeFS module from the generated module set, deletes existing uncommented `PVFSInit` lines, and appends a new directive.

## Important APIs, types, and functions
The script relies on `find`, `grep`, `awk` via `${AWK}`, Apache apxs via `${WP_APXS}`, `cat`, and `sed -i`. It derives module names by scanning `Makefile.am` files for `install:` targets containing `libmod_*.la`.

## Control flow
It builds `orangeModules`, asks `${WP_APXS} -q SYSCONFDIR` for the Apache config directory, then scans `$httpdConfig/httpd.conf` for the topmost non-commented `LoadModule` whose second token matches one of the OrangeFS module names. It removes all uncommented `PVFSInit` lines with `sed -i '/^PVFSInit/d'` and appends `PVFSInit <module>` if a matching module was found.

## State and persistence behavior
The script directly edits Apache's `httpd.conf`. It preserves commented `PVFSInit` lines only if they begin with `#`, and it appends the new directive at the end of the file rather than near the selected `LoadModule`.

## Dependencies and integration points
It integrates generated OrangeFS Apache module build metadata with Apache runtime configuration. `mod_orangefs_s3.c` uses `PVFSInit` in `orangefs_s3_post_config` to decide whether it should call `PVFS_util_init_defaults`.

## Risks and edge cases
- `${WP_APXS}` and `${AWK}` must be set and valid; no explicit validation is present.
- `sed -i` behavior differs across GNU/BSD sed.
- `sed -i '/^PVFSInit/d'` misses leading-whitespace directives and deletes all uncommented directives without preserving context.
- The `LoadModule` parser strips spaces but does not handle tabs, Apache includes, or multiline config.
- Directly editing `httpd.conf` without backup can surprise administrators.

## Test signals
Use a temporary Apache config directory from a fake `apxs` wrapper, with multiple OrangeFS `LoadModule` lines and preexisting `PVFSInit`, then verify the first loaded module is selected and only one active `PVFSInit` remains. Include tests with no matching module and commented directives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/webpack/pvfsinit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-gui/filelisthandler.cpp -->
# sources/distributed-fs/orangefs/src/client/windows/client-gui/filelisthandler.cpp

## Purpose
This C++ file implements the wxWidgets list-control helper used by the OrangeFS Windows GUI to display remote file listings and optional columns for size, permissions, and modification time.

## Important APIs, types, and functions
- `FileListHandler::FileListHandler` creates a `wxPanel` and child `wxListCtrl` sized from the global `MAIN_FRAME`.
- `getPrefixString` formats `OrangeFS_size` values into bytes/KB/MB/GB/TB strings.
- `getPermString` converts `OrangeFS_attr.perms` and `objtype` into Unix-style mode text.
- `getTimeString` formats `OrangeFS_attr.mtime` with `ctime`.
- `FileListHandler::addColumn` inserts and populates columns from `MAIN_APP` file names/attributes.
- `FileListHandler::removeColumn` deletes a column and adjusts stored column indexes.
- `FileListHandler::getSyncStatus` is a TODO stub that always returns false.

## Control flow
The main frame constructs the singleton handler, then calls `addColumn("File Name")` during startup. View-menu handlers call `addColumn` or `removeColumn` for optional columns. `addColumn` inserts a wx column, records its id in a `map<wxString,int>`, populates data according to the column name, and resizes all columns evenly. `removeColumn` resolves the id from the map, deletes the wx column, erases the map entry, resizes remaining columns, and decrements hard-coded optional column ids that were to the right of the deleted column.

## State and persistence behavior
State is in-memory GUI state only: `syncPane`, `syncList`, `syncColumnIDs`, and `localStorePath`. It reads global `MAIN_APP`/`MAIN_FRAME` state but does not persist any changes to disk. The sync status path is unimplemented.

## Dependencies and integration points
It depends on wxWidgets list controls, OrangeFS client types exposed through `main-app.h`, and the globals defined in `main-app.cpp`. It is tightly coupled to fixed display column names and `MainApp` getters.

## Risks and edge cases
- The class inherits `wxListCtrl` but actually owns a separate `wxListCtrl`; this can confuse event routing and object lifetime.
- `removeColumn` reads `this->syncColumnIDs[name]` before checking existence, which inserts a default map entry for missing names.
- `getPrefixString` can index past the four-element prefix array for sizes above TB and prints unrounded floats.
- `ctime` includes a trailing newline, which can render oddly in list cells.
- The first-column population uses `InsertItem(this->syncColumnIDs["File Name"], ...)` as item index rather than column index; because the id is zero this works accidentally.
- Destructor manually deletes wx child windows that wxWidgets may already own through parent-child lifetime management.
- `getSyncStatus` always returns false, so the status bar never reports synced files.

## Test signals
Start the GUI with 0, 1, and many file entries; toggle all optional columns in different orders; remove a non-present column; inspect size formatting around 1024 boundaries and very large sizes; verify directory/symlink permissions display correctly; select rows and confirm sync status behavior once implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-gui/filelisthandler.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-gui/filelisthandler.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-gui/filelisthandler.h

## Purpose
This header declares the singleton `FileListHandler` GUI helper and the list-control id used by the OrangeFS Windows file browser.

## Important APIs, types, and functions
`FileListHandler` publicly exposes `getInstance`, destructor, `addColumn`, `removeColumn`, `displayFileStatus`, `processListCtrlDoubleClick`, and `getSyncStatus`. It privately owns `syncList`, `syncPane`, `syncColumnIDs`, and `localStorePath`; copy and assignment are private no-op definitions.

## Control flow
Consumers call `FileListHandler::getInstance`, which lazily allocates the singleton via a private constructor. `MainFrame` owns and deletes the singleton pointer during destruction.

## State and persistence behavior
All state is process-local wxWidgets UI state. `localStorePath` is declared for future sync storage behavior but is not used by the implementation in this subset.

## Dependencies and integration points
It includes wxWidgets, C++ streams/maps, and `main-app.h`, while `main-app.h` also includes this header. Include guards prevent infinite include expansion, but the circular dependency contributes to tight coupling. Windows builds optionally include ATL time support.

## Risks and edge cases
- Singleton allocation is not thread-safe and has no reset method.
- Public methods `displayFileStatus` and `processListCtrlDoubleClick` are declared but not defined in the implementation shown, which can cause link errors if used.
- Using declarations in a header (`using std::...`) leak names into all include consumers.
- `LIST_CTRL_SYNC` is set to `0x1`, which can collide with other wx ids.

## Test signals
Build the GUI and confirm no unresolved symbols for declared methods. Exercise singleton construction/destruction across app startup/shutdown and verify event ids do not collide with main-frame menu/list ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-gui/filelisthandler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-gui/main-app.cpp -->
# sources/distributed-fs/orangefs/src/client/windows/client-gui/main-app.cpp

## Purpose
This file implements the wxWidgets OrangeFS file browser application. It initializes OrangeFS client credentials and mount entries, reads a root directory listing, creates the main frame, and wires menus to list-column visibility and configuration dialogs.

## Important APIs, types, and functions
- Globals: `MAIN_APP`, `MAIN_FRAME`, and `FileListHandler::instance`.
- `MainApp::allocateMembers` allocates root credential, file attribute array, and mount-entry array.
- `MainApp::initFileSystem` calls `orangefs_initialize` and `orangefs_load_tabfile`.
- `MainApp::OnInit` initializes wx/app state, reads root file entries with `orangefs_find_files`, creates `MainFrame`, and frees temporary listing buffers.
- `MainApp::cleanupApp` releases credentials, mount entries, and attribute arrays.
- `getLogoPath` builds a Windows path to `OrangeFS_LOGO.png` beside the executable.
- `MainFrame` constructor builds menus/status bar/icon and initializes the file list.
- Menu handlers: `onQuit`, `onAbout`, `showConfigDialog`, `showPermissions`, `showFileSize`, `showLastModified`, `onRemoteFileSelected`.

## Control flow
wxWidgets calls `MainApp::OnInit` through `IMPLEMENT_APP`. The app stores the global app pointer, allocates buffers, initializes OrangeFS with root credentials and `\\orangefstab`, enables debug logging, fetches up to `MAX_FILES` entries from `/`, stores display names in a `wxArrayString`, creates and shows `MainFrame`, and frees temporary filename buffers. The frame sets the global frame pointer, creates the singleton `FileListHandler`, sets icon/menu/status bar, and populates the initial file-name column. View menu events add or remove optional columns. Row selection asks `FileListHandler::getSyncStatus` and updates the status bar.

## State and persistence behavior
Runtime state includes root credentials, mount entries, OrangeFS attributes for up to 256 entries, GUI column state, and a selected local sync path. Persistent inputs are the tab file `\\orangefstab`, optional logo file next to the executable, and debug log output when debug is enabled. No GUI settings or sync state are persisted here.

## Dependencies and integration points
The code depends on wxWidgets 2.8-era APIs, `orangefs-client.h`, Windows path APIs for icon lookup, Visual Leak Detector (`vld.h`), and the `FileListHandler` singleton. It uses OrangeFS client debug masks and initialization functions.

## Risks and edge cases
- `debugLogFilename` is declared only under `ORANGEFS_DEBUG` but used unconditionally, which can break non-debug builds unless another declaration exists.
- `malloc` results are not checked before use in several places.
- `cleanupApp` frees all `MAX_MNTENTS` entries even if allocation failed partway.
- `orangefs_load_tabfile` is called after `orangefs_initialize` and noted as unimplemented, so mount setup may be incomplete.
- The root listing is capped at 256 files and does not paginate.
- `MAIN_FRAME` is set after `FileListHandler::getInstance` would need it; current constructor order sets `MAIN_FRAME` first, but the global dependency is fragile.
- `getLogoPath` has a possibly uninitialized `malloc_flag` if `GetModuleFileName` fails.
- Directory display appends `"   <dir>"` to the file name, which can make later operations on selected names ambiguous.

## Test signals
Build both debug and release configurations, start with missing/malformed `orangefstab`, start with more than 256 root entries, verify icon loading when the PNG is absent, toggle menu columns, choose a local sync directory, and run under leak detection through startup/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-gui/main-app.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-gui/main-app.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-gui/main-app.h

## Purpose
This header declares the wxWidgets application and main window classes for the OrangeFS Windows file browser.

## Important APIs, types, and functions
It defines menu/list ids in `enum ID`, declares `MainApp` with initialization, filesystem setup, cleanup, and getters for file listing/attributes/display dimensions, and declares `MainFrame` with menu objects, window state, local sync path, a `FileListHandler` pointer, and event handlers.

## Control flow
`MainApp::OnInit` is the wx application entry. `MainFrame` declares an event table in the implementation to bind menu and list events to the declared methods.

## State and persistence behavior
The header defines app-owned in-memory state: `fileListing`, root credential, root attributes, mount entries, file count, and display dimensions. `MainFrame` tracks menus, window size, sync path, and list handler. No persistence format is defined.

## Dependencies and integration points
It depends on wxWidgets, C runtime debug allocation headers, `orangefs-client.h`, and `filelisthandler.h`. The mutual include with `filelisthandler.h` creates tight compile-time coupling.

## Risks and edge cases
- Declares copy constructor and assignment for `MainFrame` but does not define them in the implementation shown; accidental use will fail to link.
- Getters return `short int` for counts and dimensions, which can truncate modern display sizes or larger listings.
- `getFileAttrs` returns attributes by value, which is fine for current small structs but can hide lifetime/ownership expectations.
- Header includes implementation-heavy dependencies, increasing rebuild scope.

## Test signals
Compile the GUI with strict warnings and link checks, verify event table ids align with controls, and test large display dimensions and file counts around `short int` limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-gui/main-app.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/cert.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/cert.c

## Purpose
This file loads, verifies, and converts certificate material into OrangeFS `PVFS_credential` objects for the Windows client service. It supports proxy certificates that embed UID/GID policy data and user certificates signed with local private keys for server-side identity mode.

## Important APIs, types, and functions
- OpenSSL lifecycle: `openssl_init`, `openssl_cleanup`.
- Thread-safe ex-data index helpers: `get_proxy_auth_ex_data_cred`, `get_proxy_auth_ex_data_user_name`, protected by `CRYPTO_ONCE` and `CRYPTO_RWLOCK`.
- Credential parsing: `parse_credential` accepts `uid/gid` text from proxy certificate policy data.
- Verification callback: `verify_callback` extracts proxy cert policy and initializes the output `PVFS_credential`.
- Certificate verification: `verify_cert` builds an `X509_STORE`, attaches CA cert/chain, enables proxy certs, and calls `X509_verify_cert`.
- Path helpers: `get_profile_dir`, `get_module_dir`.
- Public credential loaders: `get_proxy_cert_credential` and `get_user_cert_credential`.

## Control flow
For proxy certificates, `get_proxy_cert_credential` resolves the certificate directory from `goptions->cert_dir_prefix` or the Windows user profile, loads `cert.0` as the proxy cert and other `cert.*` files as chain certificates, loads `goptions->ca_file`, and calls `verify_cert`. During OpenSSL verification, `verify_callback` sees proxy certs, extracts `NID_proxyCertInfo`, parses the policy text as UID/GID, and initializes the credential. Successful verification duplicates the certificate expiration and gives the credential the maximum security timeout.

For user certificates, `get_user_cert_credential` resolves a key file path and certificate file path from configured paths, the module directory for `SYSTEM`, or the user's profile. It loads `orangefs-cert.pem`, converts X509 to `PVFS_certificate`, duplicates the expiration time, and calls `init_credential` with `PVFS_UID_MAX`, group `PVFS_GID_MAX`, the private key file, and attached certificate data.

## State and persistence behavior
The file reads certificate/key files from profile directories, configured certificate prefixes, module directories, and a configured CA file. It returns heap-owned credential internals through `init_credential` and an expiration `ASN1_UTCTIME` pointer used by the user cache. It also maintains process-global OpenSSL ex-data indexes and a lock.

## Dependencies and integration points
It depends on Windows profile APIs, OpenSSL X509/proxy certificate APIs, OrangeFS certificate utility functions (`PINT_load_cert_from_file`, `PINT_X509_to_cert`, `PINT_get_security_path`, `PINT_cleanup_cert`), credential initialization from `cred.c`, global `goptions`, `client_debug`, and `report_error`. It is called by `dokan-interface.c` when user mode is certificate or server.

## Risks and edge cases
- OpenSSL cleanup functions used here include APIs deprecated or changed across OpenSSL versions.
- `verify_callback` directly dereferences proxy extension fields; malformed extensions can expose null-pointer paths.
- Proxy credential parsing accepts up to 15 digits and uses `atoi`, so overflow and empty component handling are weak.
- Directory/path concatenation uses `strcpy`/`strcat`; some length checks exist but not all intermediate filenames are bounded after `FindFirstFile`.
- If loading a chain cert succeeds, ownership transfers into the stack; if a later push fails it is not handled.
- `get_proxy_cert_credential` treats `SYSTEM` as root credentials, which is operationally convenient but high trust.
- `get_user_cert_credential` sets UID/GID to max sentinel values and relies on server-side certificate handling; callers must not use those as local POSIX identities.

## Test signals
Test valid proxy certificate chains with UID/GID policies, missing `cert.0`, malformed policy strings, expired/untrusted certs, custom `cert_dir_prefix`, long profile paths, `SYSTEM` requests, user cert mode with missing key/cert, and OpenSSL initialization/cleanup under repeated service start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/cert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/cert.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/cert.h

## Purpose
This header declares Windows client-service certificate support: OpenSSL lifecycle hooks and public functions for deriving OrangeFS credentials from proxy or user certificates.

## Important APIs, types, and functions
It exposes `openssl_init`, `openssl_cleanup`, `get_proxy_cert_credential`, and `get_user_cert_credential`. Both credential functions accept a Windows user token handle, username, output `PVFS_credential`, and output certificate expiration pointer.

## Control flow
Callers initialize OpenSSL before certificate use, call one of the credential loaders according to user/security mode, cache or consume the returned credential and expiration, and eventually call `openssl_cleanup` during shutdown.

## State and persistence behavior
The header itself has no state, but its APIs allocate credential fields and an `ASN1_UTCTIME` expiration that callers must clean according to the service's credential/cache ownership rules.

## Dependencies and integration points
It includes OpenSSL ASN.1 definitions, `pvfs2.h`, and `client-service.h`, so it is bound to Windows `HANDLE` types and OrangeFS credential definitions. `dokan-interface.c` includes this header for user-mode credential lookup.

## Risks and edge cases
The header does not document ownership of `expires` or initialized credential fields. It also exposes OpenSSL types to all consumers, increasing ABI coupling.

## Test signals
Compile consumers with the target OpenSSL version and verify function prototypes match `cert.c`. Add ownership tests around returned expiration and credential cleanup in user-cache paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/cert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/client-service.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/client-service.h

## Purpose
This header defines shared Windows client-service configuration constants, the central `ORANGEFS_OPTIONS` struct, and logging/error-reporting declarations.

## Important APIs, types, and functions
- Constants: `STR_BUF_LEN`, user modes (`USER_MODE_NONE`, `LIST`, `CERT`, `LDAP`, `SERVER`), and security modes (`DEFAULT`, `KEY`, `CERT`).
- `ORANGEFS_OPTIONS`: mount point, thread count, new file/dir permissions, write-time behavior, debug settings, user/security mode, security timeout, key/private-key/certificate/CA paths.
- Functions/macros: `client_debug`, `report_error`, `_report_error`.

## Control flow
Configuration parsing fills an `ORANGEFS_OPTIONS`; service startup passes it into Dokan loop and other subsystems. Credential code reads security fields from global options. Debug helpers route messages to the configured logging mechanism.

## State and persistence behavior
This header defines the in-memory service options shape. Persistent values come from `orangefs.cfg` or environment-selected config files parsed by `config.c`.

## Dependencies and integration points
It includes `wincommon.h` for Windows types and is included by config, credential, certificate, Dokan, and other service files. The struct is an integration point between config parsing, credential creation, filesystem operations, and Dokan mount setup.

## Risks and edge cases
- Some modes are defined here but disabled or partially unsupported in `config.c`, so consumers must not assume every enum value is reachable.
- `private_key` is a `void *`, hiding OpenSSL ownership and type from the struct definition.
- Fixed `MAX_PATH` and `STR_BUF_LEN` arrays limit path and debug-mask length.
- No defaults are encoded in the type; callers must remember to call `set_defaults`/`get_config`.

## Test signals
Compile all service modules after changes to `ORANGEFS_OPTIONS`, validate config defaults populate every field consumed by Dokan/cert/cred code, and test unsupported mode values are rejected or handled consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/client-service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/config.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/config.c

## Purpose
This file parses the Windows OrangeFS client-service configuration file, populates `ORANGEFS_OPTIONS`, and seeds the user credential cache from configured user-to-UID/GID mappings.

## Important APIs, types, and functions
- Keyword table: `config_keyword_defs` maps textual options to callback functions.
- File handling: `get_module_dir`, `open_config_file`, `close_config_file`.
- Argument parsing: `get_args`, `free_args`.
- Keyword callbacks: `keyword_cb_mount`, `threads`, `user_mode`, `user`, `perms`, `write_time`, `debug`; security and LDAP callbacks are present but compiled out.
- Defaults and public API: `get_default_mount_point`, `set_defaults`, `get_config`, `add_users`.
- State: global `QLIST_HEAD(user_list)` accumulates configured users until `add_users`.

## Control flow
`get_config` opens a config file from `ORANGEFS_CONFIG_FILE`, `PVFS2_CONFIG_FILE`, or `orangefs.cfg` beside the executable. It applies defaults, reads each non-comment line, splits the keyword and argument string, finds a matching keyword definition, parses arguments with quote support, and calls the callback. After parsing, it validates required user mode and mutually exclusive debug outputs. `add_users` walks the accumulated `user_list`, initializes a credential for each `user name uid:gid` entry, and inserts it into the global user cache.

## State and persistence behavior
Persistent input is the config file. Parsed service state is stored in `ORANGEFS_OPTIONS`; configured users are temporarily stored in `user_list` and then persisted in the process user cache via `add_cache_user`. Defaults include first available drive from E: onward, permissions `0755`, list user mode, and a default debug file beside the executable.

## Dependencies and integration points
It depends on Windows drive/module APIs, OrangeFS types, `quicklist`, `security-util`, `cred.c`, and `user-cache`. `dokan-interface.c` consumes mount point, thread count, permissions, debug settings, write-time setting, and user/security modes.

## Risks and edge cases
- The keyword extraction loop uses `(*pline != ' ' || *pline == '\t')`, which does not stop on tabs as intended; it should likely use `&&`.
- `free_args` frees individual strings but not the outer `out_args` array, and `get_config` never calls `free_args`, leaking per-line allocations.
- `keyword_cb_mount` uses `strncpy` without guaranteeing null termination when input length is `MAX_PATH` or longer.
- Only `list` user mode is accepted; constants and code for cert/LDAP/server remain elsewhere, so config/service capabilities can diverge.
- `new-file-perms` rejects octal `0000`, which may be intentional but prevents no-access defaults.
- `get_config` returns early on overlong lines without closing the config file.
- `add_users` frees list entries but does not remove all links or clean remaining entries after an error.

## Test signals
Use config fixtures for valid list mode, quoted paths, tabs as separators, too many/missing args, long lines, invalid uid/gid, duplicate users, missing config file, both `debug-stderr` and `debug-file`, and no users. Verify user cache contains expected credentials and memory/leak tools show no parser leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/config.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/config.h

## Purpose
This header declares the config parser interface and internal data structures for Windows client-service configuration keywords and configured user entries.

## Important APIs, types, and functions
`CONFIG_USER_ENTRY` stores a username, PVFS UID/GID, and quicklist link. `CONFIG_KEYWORD_DEF` stores a keyword string, min/max argument counts, and callback pointer. Public functions are `get_config` and `add_users`.

## Control flow
Service startup calls `get_config` to fill `ORANGEFS_OPTIONS`, then calls `add_users` to transfer configured list-mode users into the credential cache.

## State and persistence behavior
The declared types support process-local parsed state only. Persistent data remains in the external config file.

## Dependencies and integration points
The header depends on OrangeFS types, quicklist, and `client-service.h`. It binds the parser to the service options struct and user-cache credential initialization path.

## Risks and edge cases
The callback type exposes parser internals and mutable `char **args` to callbacks. Fixed `STR_BUF_LEN` in `CONFIG_USER_ENTRY` caps usernames. The header does not expose `set_defaults`, so tests or alternate startup paths cannot call it directly without reaching into `config.c`.

## Test signals
Compile parser callbacks against this signature, run startup tests that call `get_config`/`add_users`, and validate long usernames are truncated safely and consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/cred.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/cred.c

## Purpose
This file creates, signs, copies cleanup responsibility for, and queries OrangeFS `PVFS_credential` objects used by the Windows client service.

## Important APIs, types, and functions
- `get_system_credential` creates a root uid/gid credential for the Windows `SYSTEM` user or fallback system operations.
- `sign_credential` reads or reuses an OpenSSL private key and signs stable credential fields with SHA1.
- `init_credential` allocates issuer/group/certificate/signature fields and applies security-mode-dependent signing.
- `cleanup_credential` frees fields allocated by `init_credential`.
- `credential_in_group` checks group membership.
- Disabled helpers show prior support for adding groups and setting timeout.

## Control flow
Callers allocate a `PVFS_credential` struct and call `init_credential`. It zeroes the struct, allocates an issuer string prefixed `C:` plus the local hostname, allocates and copies group ids, sets UID and long timeout, optionally attaches certificate bytes, and signs when `goptions->security_mode` is key or certificate. On failure it cleans allocated fields. `sign_credential` chooses a cached private key in key mode or loads a PEM key file, signs uid, group count, groups, issuer, and timeout, and stores signature bytes plus size.

## State and persistence behavior
Credentials are heap-backed and caller-owned. Signing may read persistent PEM key files. `goptions->private_key`, `security_mode`, and `key_file` influence behavior. Credential timeout is set to `time(NULL) + PVFS2_SECURITY_TIMEOUT_MAX`.

## Dependencies and integration points
It depends on OpenSSL EVP/PEM, OrangeFS request protocol types, `pint-util`, global `goptions`, Windows sockets hostname APIs, and service logging. `config.c`, `cert.c`, and `dokan-interface.c` all depend on these credential helpers.

## Risks and edge cases
- SHA1 signing is legacy and may be unacceptable in stricter security contexts.
- `EVP_MD_CTX_new` is not checked for null before use.
- `sign_credential` returns raw `errno` on key-file open failure after reporting a mapped PVFS error, while most callers expect negative PVFS/Windows-style errors.
- `cleanup_credential` does not free `cred->certificate.buf`, so certificate mode can leak attached certificate data.
- `init_credential` uses `gethostname` but assumes Winsock is initialized by the service.
- Timeout is always maximum, with TODO comments about server timeout/caching revision.

## Test signals
Test default root credential, list-mode unsigned credentials, key-mode signing with valid/missing/invalid PEM keys, cert-mode with attached certificate bytes, cleanup under all modes with leak detection, and hostname failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/cred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/cred.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/cred.h

## Purpose
This header declares the Windows client-service credential helper API.

## Important APIs, types, and functions
Public declarations include `init_credential`, `cleanup_credential`, `credential_in_group`, and `get_system_credential`. Commented declarations document disabled `credential_add_group` and `credential_set_timeout` helpers.

## Control flow
Callers allocate a `PVFS_credential`, initialize it through `init_credential` or `get_system_credential`, pass it to OrangeFS filesystem calls, then release dynamic fields with `cleanup_credential` or `PINT_cleanup_credential` as appropriate.

## State and persistence behavior
The API initializes heap-owned fields inside caller-provided structs. Persistent key/certificate reads are controlled by the implementation and global options, not by this header.

## Dependencies and integration points
It includes OrangeFS credential and request protocol definitions. Config, certificate, user-cache, and Dokan code use the declarations to construct request credentials.

## Risks and edge cases
The header does not declare `sign_credential` even though it is externally linkable in `cred.c`; this limits intended public API but leaves a non-static symbol. Ownership expectations around certificate buffers are not documented.

## Test signals
Compile all service modules against this header with warnings for missing prototypes, and add API-level tests that pair every successful initialization with cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/cred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/dokan-interface.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/dokan-interface.c

## Purpose
This file is the Windows Dokan bridge for OrangeFS. It registers Dokan filesystem callbacks, converts Windows paths/attributes/security requests to OrangeFS operations, maps errors, resolves per-request credentials, caches open-context credentials/object references, and starts the long-running Dokan mount loop.

## Important APIs, types, and functions
- Debug/error helpers: `client_debug`, `error_map`.
- Encoding/path helpers: `convert_wstring`, `convert_mbstring`, `get_fs_path`, `convert_pvfstime`, `convert_filetime`.
- Credential path: `get_requestor_credential`, `get_credential`, `add_context`, `get_context_entry`, `remove_context`, `cred_compare`.
- Permission helpers: `check_perm`, `check_create_perm`, `PVFS_sys_attr_to_file_info`.
- Dokan callbacks: `PVFS_Dokan_create_file`, `create_directory`, `open_directory`, `close_file`, `cleanup`, `read_file`, `write_file`, `flush_file_buffers`, `get_file_information`, `set_file_attributes`, `find_files_with_pattern`, `delete_file`, `delete_directory`, `move_file`, `lock_file`, `set_end_of_file`, `set_allocation_size`, `set_file_time`, security callbacks, `unmount`, `get_disk_free_space`, `get_volume_information`.
- Entrypoint: `dokan_loop` builds `DOKAN_OPTIONS`/`DOKAN_OPERATIONS` and repeatedly calls `DokanMain`.

## Control flow
`dokan_loop` initializes a qhash context cache and mutex, maps service debug settings into global flags and Dokan options, converts the mount point, assigns callbacks, and enters a retry loop around `DokanMain`, sleeping 30 seconds after each exit.

For each filesystem callback, paths are converted from wide chars to multibyte and resolved through `fs_resolve_path`. Credentials are fetched either from `DokanFileInfo->Context` via `context_cache` or from the requestor token with `DokanOpenRequestorToken`. Cache misses are resolved through list-mode user cache, proxy certificate mode, LDAP mode, server/user certificate mode, or system credentials. Open/create callbacks generate a unique context and cache a copied credential. Close removes context and applies delete-on-close removal.

Read/write use an IO cache when enabled: the first operation resolves object refs with `fs_lookup`, then subsequent operations use `fs_read2`/`fs_write2` by object ref. Attribute and directory callbacks translate PVFS attributes to Windows `BY_HANDLE_FILE_INFORMATION`/`WIN32_FIND_DATAW`. Delete operations only validate lookup and defer actual removal to close. Move maps to `fs_rename`; allocation size maps to `fs_truncate`; set-file-time maps FILETIME values into PVFS setattr masks.

## State and persistence behavior
Persistent state is the mounted OrangeFS namespace. Runtime state includes global debug flags, global `goptions`, `context_cache` keyed by Dokan context ids with copied credentials and open flags, optional IO cache entries keyed by context, and the Dokan mount loop. File metadata changes persist through `fs_setattr`, writes persist through `fs_write2`/`fs_write`, deletes through `fs_remove`, and renames through `fs_rename`.

## Dependencies and integration points
The file integrates Dokan 0.6-style APIs, Windows token/SID/security APIs, OrangeFS/PVFS2 filesystem wrapper functions from `fs.h`, credential/cert/user-cache/LDAP helpers, quickhash/gen-locks, gossip debug logging, and IO cache support. It is the primary consumer of `ORANGEFS_OPTIONS` produced by `config.c`.

## Risks and edge cases
- `dokan_loop` retries forever and cleanup code after the loop is unreachable under normal operation.
- Context ids from `QueryPerformanceCounter` can collide in theory and are not checked for existing qhash entries.
- `get_requestor_credential` calls `CloseHandle(htoken)` even after the no-requestor branch may leave `htoken` invalid or uninitialized in some paths.
- `PVFS_Dokan_delete_directory` calls `add_context` before `PVFS_Dokan_delete_file`, while `DokanFileInfo->Context` may be zero; qhashing context zero can collide with other uninitialized contexts.
- Permission checks are client-side approximations and server mode intentionally returns permission if any class has the bit, relying on server enforcement.
- `PVFS_Dokan_set_end_of_file` returns success without truncating; Windows callers may expect EOF changes to persist.
- `PVFS_Dokan_move_file` ignores `ReplaceIfExisting`.
- `PVFS_Dokan_get_file_security` is marked crash-prone and not registered for get, while set security is a no-op success.
- Several buffer copies use `wcscpy`/`wcsncpy` without checking destination sizes from Dokan buffers.
- IO cache cleanup/update code in `PVFS_Dokan_cleanup` is disabled, so cached IO entries may rely on external cleanup behavior and access times may not update on reads.

## Test signals
Run Dokan mount smoke tests for create/open/read/write/flush/close/delete, delete-on-close for files and directories, rename with existing target and `ReplaceIfExisting`, set allocation and EOF semantics, directory listing with wildcard patterns and more than 60 entries, permission-denied cases for owner/group/other, credential cache hit/miss across Windows users, service startup before network availability, and forced `DokanMain` failures to observe retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/dokan-interface.c -->
