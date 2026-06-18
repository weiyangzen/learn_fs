Grouped research for `subset-b-007790`. Each section preserves the original source path and is delimited for deterministic splitting into source-tree-aligned per-file research reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.m

Purpose: implements the OpenAFS macOS preference pane controller. It owns the main preference UI, authorization lock integration, CellServDB table, token table, cache-parameter controls, symlink table, background menu activation, and modal sheets for IP editing, credentials, info, and link creation.

Important APIs and control flow: `initWithBundle:` initializes startup sizing state. `mainView` adjusts the pane width for Mac OS X 10.5+. `mainViewDidLoad` wires table delegates and configures `SFAuthorizationView` for `kAuthorizationRightExecute`. `didSelect` installs/repairs the backgrounder LaunchAgent, reads CFPreferences, creates `AFSPropertyManager`, registers distributed and workspace notifications, refreshes AFS state, loads configuration, and filters CellServDB. `willUnselect` writes preferences, releases arrays/managers, unregisters notifications, and stops token polling.

State and persistence: UI state is backed by `CFPreferences` keys from `global.h`, including aklog use, token-at-login, startup, menu visibility, link enablement, link plist data, and Kerberos renew timing. AFS client configuration is delegated to `AFSPropertyManager`, which reads and writes `/var/db/openafs` files through `TaskUtil` and the privileged helper. Runtime state includes `filteredCellDB`, `tokenList`, `tokensLock`, and `timerForCheckTokensList`.

Dependencies and integration: depends on Cocoa/PreferencePanes, SecurityInterface authorization, `PListManager`, `TaskUtil`, `AFSPropertyManager`, `IpConfiguratorCommander`, `TokenCredentialController`, `InfoController`, `LynkCreationController`, and `NSString+search`. It posts distributed notifications to `it.infn.lnf.network.AFSBackgrounder` so the background menu app updates tokens, preferences, and AFS state.

Risks: table and selection code assumes filtered row indexes remain valid while removing cells. Many methods use manual retain/release and several copied CF objects are not explicitly released. `refreshTokens:` relies on a nonblocking lock but updates UI after shelling out to `tokens`. The mount notification checks `NSDevicePath == /afs` even though cacheinfo may configure another mount point. Startup and service status depend on privileged helper return values and legacy `launchctl` behavior.

Test signals: exercise pane selection/unselection, authorization lock/unlock, load/save of CFPreferences, startup toggle, start/stop AFS, token refresh with empty and populated `tokens` output, `aklog` and klog flows, CellServDB filtering/removal/editing, symlink add/remove persistence, backgrounder LaunchAgent creation when `~/Library/LaunchAgents` is missing, and mount/unmount notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSPropertyManager.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSPropertyManager.h

Purpose: declares the model/service object used by the preference pane to read, mutate, and persist OpenAFS client configuration, daemon state, CellServDB entries, cache manager parameters, and token operations.

Important APIs and types: `AFSPropertyManager` stores `installationPath`, default cell name, mutable `cellList`, user token-default cells, cacheinfo fields, afsd option flags, `FileUtil`, and `useAfsdConfVersion`. Public methods cover initialization, getters/setters for cache manager knobs, `loadConfiguration`, `clearConfiguration`, `readCellInfo`, `readCellDB`, `readTheseCell`, `saveConfigurationFiles:`, `saveCacheConfigurationFiles:`, `startup`, `shutdown`, `checkAfsStatus`, `getTokenList`, `klog`, `aklog`, `getTokens`, `unlog`, and `makeChaceParamString`.

State and persistence: constants identify legacy startup scripts, launchd plist names, AFS mount strings, `/var/db/openafs` as the default base, old `afsd.options`, new `afs.conf`, `cacheinfo`, `ThisCell`, `CellServDB`, and `TheseCells`. The header is the contract between UI controllers and the privileged helper path.

Dependencies and integration: imports `DBCellElement` for CellServDB rows and `FileUtil` for older Authorization Services file operations. The implementation additionally integrates `TaskUtil` and Kerberos helpers.

Risks: method comments document old and new config formats, but no validation contract is exposed for numeric ranges or path safety. Header names contain typos (`makeChaceParamString`) that are ABI/API visible. Consumers can mutate the returned `NSMutableArray *` directly.

Test signals: compile all declarations against callers, verify old/new afsd option selection by OpenAFS version, cover direct mutation of `getCellList`, and check that all privileged write callers use only paths accepted by the helper allowlist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSPropertyManager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSPropertyManager.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSPropertyManager.m

Purpose: implements the preference pane's OpenAFS configuration engine. It parses local AFS configuration from `/var/db/openafs`, exposes cache and cell state to the UI, writes changed config through the privileged helper, starts/stops the client, and shells out for tokens.

Important APIs and control flow: `loadConfiguration` checks the install path, clears current state, determines whether to use `afs.conf` or `afsd.options` from `fs -version`, reads `ThisCell`, `TheseCells`, `CellServDB`, `cacheinfo`, and afsd options. `readCellDB` scans `CellServDB` into `DBCellElement` and `CellIp` objects. `readAFSDParamLineContent` decodes `-afsdb`, `-verbose`, `-stat`, `-dcache`, `-daemons`, `-volumes`, and `-dynroot`. `saveConfigurationFiles:` writes `ThisCell`, `CellServDB`, and `TheseCells`; `saveCacheConfigurationFiles:` writes `cacheinfo` plus old or new afsd config. `getTokens:` iterates token-default cells and calls klog or aklog.

State and persistence: persistent state lives in OpenAFS config files under `/var/db/openafs/etc` and `/var/db/openafs/etc/config`, but callers pass logical names like `/etc/CellServDB` to `TaskUtil`; the privileged helper prefixes them with `/var/db/openafs`. Backups use `.afscommander_bk`. AFS status is inferred from mounted volume resource descriptions containing `(afs)`.

Dependencies and integration: uses `TaskUtil` for `fs`, `tokens`, `klog`, `aklog`, `unlog`, privileged backup/write, `afsd_start`, and `afsd_stop`. Uses `Krb5Util` to acquire tickets before `aklog`. Exposes mutable `cellList` directly to `AFSCommanderPref` and `IpConfiguratorCommander`.

Risks: parsers are scanner-based and fragile around comments, quoted values, empty files, malformed lines, hostnames without IPs, and missing `TheseCells` because `readTheseCell` assumes a nonnil file handle. Version parsing shells out to `fs` multiple times. `klog` compares strings with `== @""`, not content equality. `checkAfsStatus` ignores the configured mount point. Privileged writes accept only the helper allowlist; adding new files requires updating both sides.

Test signals: fixtures for `ThisCell`, empty/missing `TheseCells`, CellServDB entries with no servers, comments and whitespace, old and new afsd configs, malformed `fs -version`, cacheinfo validation, backup/write failures, start/stop status codes, token parsing, multi-cell token acquisition, and mounted-volume detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSPropertyManager.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AuthUtil.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AuthUtil.h

Purpose: declares a singleton wrapper around macOS Authorization Services used by the preference pane and older file utilities to obtain, store, serialize, and use an `AuthorizationRef`.

Important APIs and state: `AuthUtil` stores `authorizationRef` and `isAuthorizationRefOwned`. It exposes `autorize`, `deautorize`, `authorization`, `setAuthorization:`, `extFormAuth`, `execUnixCommand:args:output:`, and singleton/memory-management overrides. The spelling of `autorize`/`deautorize` is part of the local API.

Control flow and persistence: no persistent storage is declared; the object is process-global runtime state. The `SFAuthorizationView` delegate in `AFSCommanderPref.m` injects an authorization reference via `setAuthorization:` so `TaskUtil` can serialize it for the XPC privileged helper.

Dependencies and integration: imports Cocoa and Security Authorization headers. Older `FileUtil` operations call `execUnixCommand`, while newer root tasks flow through `TaskUtil` and the XPC helper.

Risks: singleton lifetime and retain-count overrides assume manual reference counting. Callers must not outlive an externally owned `AuthorizationRef`. The API still exposes `AuthorizationExecuteWithPrivileges`-style execution, which is deprecated and higher risk than the helper-based path.

Test signals: verify singleton identity, external authorization replacement, owned authorization cleanup, external-form serialization failure behavior, and command execution with and without output capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AuthUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AuthUtil.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AuthUtil.m

Purpose: implements the singleton Authorization Services bridge for privileged operations.

Important APIs and control flow: `shared` lazily allocates the singleton through `allocWithZone:`. `autorize` first tries `AuthorizationCopyRights` on any existing ref, creates one if absent, and requests `kAuthorizationRightExecute` with interaction/preauthorization/extend-rights flags. `deautorize` frees owned refs. `setAuthorization:` releases an internally owned ref before adopting an external one. `extFormAuth` calls `AuthorizationMakeExternalForm`. `execUnixCommand:args:output:` uses `AuthorizationExecuteWithPrivileges`, reads the returned pipe into an optional `NSMutableString`, closes the stream, and waits for a child.

State and persistence: state is only in-process. The singleton may either own the ref it created or borrow a ref supplied by the preference pane authorization view.

Dependencies and integration: used by `TaskUtil` for authorization and by `FileUtil`/`PListManager` for older privileged file manipulation. Depends on Security.framework and POSIX `read`/`wait`.

Risks: `AuthorizationExecuteWithPrivileges` is deprecated and the `wait()` call may reap unrelated children. The output append uses a fixed buffer as a C string without explicitly null-terminating each read. `authorizationRef` can be nil when `AuthorizationCopyRights` is first called. Manual singleton retain overrides complicate ownership analysis.

Test signals: denied authorization, user-cancel paths, borrowed vs owned refs, serialization with nil refs, command output larger than 1024 bytes, nonzero command exits, and concurrent singleton acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AuthUtil.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/CellIp.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/CellIp.h

Purpose: declares the small model object representing one CellServDB server address and comment.

Important APIs and state: `CellIp` contains `NSString *ip` and `NSString *ipComment`. It exposes initialization, deallocation, setters/getters for address and comment, and `description` for serializing back to CellServDB line format.

Control flow and persistence: persistence is indirect. `AFSPropertyManager` constructs `CellIp` instances while parsing `CellServDB`, `IpConfiguratorCommander` edits them in the IP table, and `DBCellElement description` serializes them for privileged writeback.

Dependencies and integration: imports Cocoa only. It is owned by `DBCellElement` arrays and consumed by UI table delegates.

Risks: the class performs no validation of IP address or hostname syntax. Manual retain/release means initial literal defaults and later retained strings must be handled carefully.

Test signals: construction defaults, setters with nil/non-nil values, description formatting, memory management under repeated edits, and serialization round trips through `DBCellElement`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/CellIp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/CellIp.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/CellIp.m

Purpose: implements the CellServDB server-address model.

Important APIs and control flow: `init` sets defaults `0.0.0.0` and `-----`; setters release old values and retain the new strings; getters return the stored strings; `description` builds `ip #comment\n`.

State and persistence: the object is a mutable in-memory row. Persistence occurs when `DBCellElement` concatenates `CellIp description` into CellServDB content and `AFSPropertyManager` writes it via `TaskUtil executePrivTaskWrite`.

Dependencies and integration: directly integrated by `DBCellElement`, `AFSPropertyManager scanIpForCell:allIP:`, and `IpConfiguratorCommander` table editing.

Risks: releasing string literals assigned in `init` is unsafe under manual memory management if the object is deallocated before setters replace them. The class does not escape comments or reject newlines, so malformed user input can corrupt CellServDB serialization.

Test signals: dealloc after default initialization, edited IP/comment values, newline/comment injection, empty strings, and CellServDB parse/serialize round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/CellIp.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/DBCellElement.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/DBCellElement.h

Purpose: declares the model object for an AFS CellServDB cell, including default-token flags, default-cell flag, name, comment, and server list.

Important APIs and state: fields are `userDefaultForToken`, `userDefaultCell`, `cellName`, `cellComment`, and `ipCellList`. Public methods set/get cell name and comment, set/query token default and default cell flags, add/get `CellIp` entries, serialize via `description`, and compare via `isEqual:`/`isEqualToString:`.

Control flow and persistence: `AFSPropertyManager` populates these objects from `ThisCell`, `TheseCells`, and `CellServDB`; `AFSCommanderPref` displays and toggles flags; `IpConfiguratorCommander` edits cell metadata and IPs; `AFSPropertyManager saveConfigurationFiles:` writes each `description`.

Dependencies and integration: imports Cocoa and `CellIp.h`. The mutable IP array is exposed directly for table editing.

Risks: the object has no validation for CellServDB grammar, duplicate cell names, default-cell uniqueness, or server list validity. Direct mutable array exposure allows callers to bypass invariants.

Test signals: default flags, unique default-cell assignment through `AFSPropertyManager`, equality behavior, empty/duplicate IP lists, and serialization of comments and addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/DBCellElement.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/DBCellElement.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/DBCellElement.m

Purpose: implements CellServDB cell storage and serialization.

Important APIs and control flow: `init` initializes flags false and allocates `ipCellList`. Setters retain strings after releasing old values. `addIpToCell:` appends a `CellIp`. `description` emits `>cell #comment\n` followed by each server line. `isEqual:` compares name and comment; `isEqualToString:` compares a string to the cell name.

State and persistence: this is the in-memory representation that becomes the persisted `CellServDB` file. The token/default-cell flags are not serialized into CellServDB; they are used to derive `ThisCell` and `TheseCells` during save.

Dependencies and integration: used by `AFSPropertyManager`, `AFSCommanderPref`, and `IpConfiguratorCommander`.

Risks: `description` returns a retained `NSMutableString` without autorelease, which can leak when callers append it without releasing. `isEqual:` assumes `anObject` responds to `getCellName` and `getCellComment`. It cannot represent comments containing newlines safely.

Test signals: serialization exactness, retain/release under repeated edits, equality with non-DBCellElement objects, empty comments, and correct persistence of default-cell/token flags through `AFSPropertyManager`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/DBCellElement.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/FileUtil.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/FileUtil.h

Purpose: declares an older privileged file-operation helper for moving, copying, deleting, and changing ownership using Authorization Services.

Important APIs and state: `FileUtil` has an `AuthUtil *autorization` ivar but the implementation uses `[AuthUtil shared]` directly. Methods are `autorizedMoveFile:toPath:`, `autorizedChown:owner:group:`, `autorizedCopy:toPath:`, and `autorizedDelete:`.

Control flow and persistence: callers build a temp file or modified plist and use this helper to copy/move/chown it into privileged locations, especially `/etc/authorization` in `PListManager`.

Dependencies and integration: imports Cocoa and `AuthUtil.h`. It predates the XPC privileged helper used by `TaskUtil`.

Risks: file paths are caller-provided and not allowlisted here. The misspelled method names are public local API. Security depends entirely on the AuthorizationRef held by `AuthUtil`.

Test signals: successful/denied authorization, paths with spaces, chown owner/group formatting, copy without overwrite expectations, and delete failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/FileUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/FileUtil.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/FileUtil.m

Purpose: implements the legacy Authorization Services file operation wrapper.

Important APIs and control flow: each method builds a null-terminated argv array and calls `[[AuthUtil shared] execUnixCommand:args:output:nil]` for `/bin/mv`, `/bin/cp`, `/usr/sbin/chown`, or `/bin/rm`. `autorizedChown:` constructs `owner:group` dynamically.

State and persistence: no local persistent state. Effects are direct filesystem mutations performed with elevated privileges.

Dependencies and integration: used by `PListManager krb5TiketAtLoginTime:` when modifying `/etc/authorization`. It uses `AuthUtil`'s deprecated privileged execution path instead of the safer XPC helper.

Risks: arbitrary source/destination paths are accepted. No `--` delimiter is used before paths, so paths beginning with `-` can be interpreted as options. There is no atomic write protocol beyond what callers implement. Error propagation is only an `OSStatus`.

Test signals: move/copy/chown/delete success and denial, path option-injection cases, nonexistent source/destination, ownership failure, and preserving backups around `/etc/authorization`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/FileUtil.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Info.plist.in -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Info.plist.in

Purpose: plist template for the `OpenAFS.prefPane` bundle.

Important keys: identifies the bundle as `it.infn.lnf.network.openafs`, package type `BNDL`, principal class `AFSCommanderPref`, main nib `OpenAFSPreference`, icon `AFSCommanderIcon`, and displayed preference pane label `OpenAFS`. `SMPrivilegedExecutables` declares the embedded helper `org.openafs.privhelper` and the code-signing requirement for helper installation.

State and persistence: this file becomes bundle metadata at build/install time. The `@MACOS_TEAM_ID@` substitution controls the Team ID requirement for helper authorization.

Dependencies and integration: consumed by Xcode/build tooling and ServiceManagement. It must match `TaskUtil`'s `PRIVHELPER_ID` and `PrivilegedHelper/privhelper-info.plist.in`'s client requirements.

Risks: bundle identifier mismatch breaks CFPreferences domains and distributed notifications. Incorrect Team ID substitution prevents SMJobBless/helper authorization. Legacy version strings are static.

Test signals: built bundle has expected identifiers, `NSPrincipalClass` loads, nib exists, helper requirement matches the signed helper, and ServiceManagement accepts the `SMPrivilegedExecutables` entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Info.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/InfoController.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/InfoController.h

Purpose: declares the controller for the preference pane's information/license sheet.

Important APIs and state: stores `infoPanel`, `texEditInfo`, and `htmlLicence`. Exposes `closePanel:` and `showHtmlResource:`. The implementation loads RTF data into a text view.

Control flow and persistence: no persistent state; the controller is created from a nib and used by `AFSCommanderPref info:` to display the bundled license resource as a modal sheet.

Dependencies and integration: imports Cocoa and is driven by the `Info` sheet outlets in `AFSCommanderPref`.

Risks: outlet names are untyped `id`, so nib wiring errors are compile-time invisible. The retained attributed string must be released on close to avoid leaks.

Test signals: nib outlet binding, loading missing/valid RTF resources, repeated open/close cycles, and modal sheet closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/InfoController.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/InfoController.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/InfoController.m

Purpose: implements the information sheet controller.

Important APIs and control flow: `awakeFromNib` clears `htmlLicence`. `showHtmlResource:` reads file data from `resourcePath`, initializes an `NSAttributedString` with RTF data, and installs it in the text view's storage. `closePanel:` releases the attributed string and ends the sheet.

State and persistence: holds only the current attributed license content in memory.

Dependencies and integration: called by `AFSCommanderPref info:` with the bundle's `license.rtf` path. Depends on Cocoa text storage APIs.

Risks: repeated `showHtmlResource:` calls before `closePanel:` leak the previous `htmlLicence`. Missing or invalid RTF data can produce nil behavior without user feedback. Outlet casts assume `texEditInfo` is an `NSTextView`.

Test signals: valid RTF rendering, missing file behavior, repeated show/close cycles, and close button ending the correct sheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/InfoController.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/IpConfiguratorCommander.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/IpConfiguratorCommander.h

Purpose: declares the sheet controller used to edit one `DBCellElement` and its server IP/comment list.

Important APIs and state: stores panel/UI outlets, `hasSaved`, target `DBCellElement *cellElement`, backup/work IP arrays, and current selected IP. Methods include `setWorkCell:`, save/cancel, create/delete IP, `saved`, `getPanel`, `commitModify`, `rollbackModify`, `loadValueFromCellIPClass`, and `manageTableSelection:`.

Control flow and persistence: edits are staged in `workIPArray` while the sheet is open, then committed back to the cell model. Persistence to disk is later performed by `AFSPropertyManager saveConfigurationFiles:`.

Dependencies and integration: imports `DBCellElement` and `AFSCommanderPref`. Used by the main pane when a CellServDB row is double-clicked or the IP button is pressed.

Risks: the header imports the main controller, creating tight coupling. The backup/work array naming hides that the object mutates the same `CellIp` instances in the shallow copy.

Test signals: opening with nil/non-nil cell, save vs cancel, add/delete rows, table edits, and subsequent CellServDB save serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/IpConfiguratorCommander.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/IpConfiguratorCommander.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/IpConfiguratorCommander.m

Purpose: implements the CellServDB IP edit sheet.

Important APIs and control flow: `awakeFromNib` makes the IP table use this object as delegate/data source. `windowDidBecomeKey:` validates `cellElement`, assigns `bkIPArray` from `[cellElement getIp]`, shallow-copies it to `workIPArray`, and loads text fields. `save:` marks saved, commits cell name/comment and replaces `bkIPArray` contents with `workIPArray`. `cancel:` releases the work array. Table data source methods expose two columns for IP and comment and write edits into `CellIp` objects.

State and persistence: changes remain in memory until the parent pane writes configuration. Because the work array is a shallow copy, editing an existing `CellIp` mutates the original even before save; cancel only discards array membership changes, not edited object fields.

Dependencies and integration: consumed by `AFSCommanderPref modifyCell:` sheet lifecycle. Uses `CellIp` and `DBCellElement`.

Risks: cancel semantics are incomplete for edited existing IP/comment rows. `createNewIP:` scrolls using `[cellElement getIp] count` instead of `workIPArray` count. No validation for cell name, IP, hostname, comment, or duplicate servers.

Test signals: save and cancel after editing existing row values, add/delete before cancel, empty IP rows, invalid comments/newlines, nil cell handling, and parent table refresh after sheet closes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/IpConfiguratorCommander.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Krb5Util.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Krb5Util.h

Purpose: declares Kerberos helper APIs for acquiring and renewing tickets before AFS token acquisition.

Important APIs: `+getNewTicketIfNotPresent` ensures there are valid Kerberos tickets, and `+renewTicket:renewTime:` renews tickets when expiration is near. The class imports both legacy KerberosLogin and Kerberos headers.

Control flow and persistence: no local persistence. It operates on the user's default Kerberos credential cache and login dialogs.

Dependencies and integration: `AFSPropertyManager aklog:noKerberosCall:` calls `getNewTicketIfNotPresent` before running `aklog`. Backgrounder code can use renew preferences defined in `global.h`.

Risks: KerberosLogin APIs are legacy and gated by SDK version macros. Caller behavior depends on interactive login availability.

Test signals: valid ticket cache, empty cache with successful login, user cancel, expired-but-renewable ticket, nonrenewable ticket, and SDK-version-specific compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Krb5Util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Krb5Util.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Krb5Util.m

Purpose: implements Kerberos ticket acquisition and renewal for aklog workflows.

Important APIs and control flow: `getNewTicketIfNotPresent` calls `KLCacheHasValidTickets`, creates login options when no valid tickets exist, copies default login options on older SDKs, then calls `KLAcquireNewInitialTickets`. It throws for non-cancel Kerberos failures. `renewTicket:renewTime:` creates login options, reads current ticket expiration, and renews when seconds-to-expire is below the threshold. On newer SDKs it uses raw krb5 APIs to get renewed creds and store them; on older SDKs it uses `KLRenewInitialTickets`.

State and persistence: mutates the user's default Kerberos credential cache. No application-level state is stored.

Dependencies and integration: Foundation, KerberosLogin, Kerberos/krb5, dispatch once for krb5 context. Used by `AFSPropertyManager` before `aklog`.

Risks: error handling overwrites `kstatus` several times and may miss intermediate failures. Some krb5 resources such as creds contents are not fully freed in the visible code. SDK macro branches mean behavior differs across build targets. Interactive acquisition can block UI callers.

Test signals: no-ticket acquisition, user-cancel nonthrow behavior, default login option propagation, near-expiry renewal, krb5 cache store failures, and old/new SDK compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Krb5Util.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/LynkCreationController.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/LynkCreationController.h

Purpose: declares the symlink/link configuration sheet controller used by the preference pane link tab.

Important APIs and state: stores `lynkCreationSheet`, destination path and link-name text fields, and `choiceResult`. Exposes `getView`, `save:`, `cancell:`, and `selectLinkDest:`.

Control flow and persistence: the implementation writes link-name to destination-path mappings into the preference domain under `PREFERENCE_LINK_CONFIGURATION`.

Dependencies and integration: imports Cocoa and depends on constants from `global.h` in the implementation. `AFSCommanderPref` opens the sheet and reloads link configuration on close.

Risks: spelling of class/file uses `Lynk`, and `cancell:` is misspelled. Header does not document expected path semantics or duplicate-name behavior.

Test signals: nib outlet wiring, empty fields, duplicate link names, directory picker selection/cancel, and CFPreferences round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/LynkCreationController.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/LynkCreationController.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/LynkCreationController.m

Purpose: implements adding a named link mapping to preference storage.

Important APIs and control flow: `save:` rejects blank trimmed destination or name, loads existing `PREFERENCE_LINK_CONFIGURATION` plist data from CFPreferences, creates a mutable dictionary if absent, stores destination path under link name, serializes XML plist data, writes it back to the current user's preference domain, synchronizes, and ends the sheet. `cancell:` ends the sheet. `selectLinkDest:` opens a directory-only `NSOpenPanel` and copies the selected path into the destination field.

State and persistence: persistent link configuration is a dictionary serialized as XML plist data in CFPreferences for `it.infn.lnf.network.openafs`.

Dependencies and integration: used by `AFSCommanderPref addLink:` and `didEndSymlinkSheet:`. Link enablement and table display are handled in the main controller.

Risks: no validation for link name characters, existing destination existence after selection, duplicates beyond overwriting, or stale preference data. `propertyListFromData` return is assigned to `NSMutableDictionary *` but may be immutable depending on API behavior.

Test signals: first link creation, appending to existing plist, duplicate overwrite, invalid/blank fields, directory selection cancel, and reloading in the parent link table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/LynkCreationController.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/NSString+search.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/NSString+search.h

Purpose: declares a small `NSString` category for extracting a substring delimited by start and end tokens.

Important API: `-estractTokenByDelimiter:endToken:` scans the receiver for an optional start token and required end token and returns the extracted substring.

Control flow and persistence: no persistence. The main known caller is `AFSCommanderPref unlog:`, which extracts a cell name from a token description line between `afs@` and a following space.

Dependencies and integration: imports Cocoa and extends all NSString instances in this bundle.

Risks: method name is misspelled. The contract does not specify behavior when delimiters are missing or repeated.

Test signals: token string with expected delimiters, missing start token, missing end token, multiple spaces, multiple `afs@` substrings, and empty receiver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/NSString+search.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/NSString+search.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/NSString+search.m

Purpose: implements the delimiter-extraction category used for token parsing.

Important APIs and control flow: creates an `NSScanner` over `self`, optionally scans up to `startToken`, scans up to `endTk` into `result`, and strips the start token length from the front if a start token was supplied.

State and persistence: stateless string utility.

Dependencies and integration: used by `AFSCommanderPref` to derive a cell name from a token row before invoking `unlog -c`.

Risks: if `startToken` is absent, `result` may not contain the expected prefix and `substringFromIndex:` can raise. If `endTk` is absent, the method returns nil. The method does not advance past the start token explicitly, so scanner behavior is fragile.

Test signals: expected token row format, absent delimiters, short strings that trigger substring bounds issues, nil end token, and token rows with trailing punctuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/NSString+search.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/PListManager.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/PListManager.h

Purpose: declares static utilities for modifying macOS authorization and launchd plist configuration used by OpenAFS login/startup/backgrounder features.

Important APIs and constants: constants define login mechanism strings for 10.4 and 10.5+, `/etc/authorization` paths, temp/backup files, backgrounder LaunchAgent labels/paths, and AFS startup LaunchDaemon paths. Methods include `krb5TiketAtLoginTime:helper:`, `checkKrb5AtLoginTimeLaunchdEnable`, `installBackgrounderLaunchdFile:resourcePath:`, `checkLoginTimeLaunchdBackgrounder`, `manageAfsStartupLaunchdFile:afsStartupScript:afsBasePath:afsdPath:`, `launchctlCommand:userDomain:option:plistName:`, and `launchdJobState:`.

State and persistence: persistent effects are edits to `/etc/authorization`, user LaunchAgents under `~/Library/LaunchAgents`, and LaunchDaemon-style startup plists.

Dependencies and integration: implemented with `FileUtil`, `TaskUtil`, Cocoa plist serialization, and `launchctl`. Called by `AFSCommanderPref`.

Risks: system authorization database formats changed across macOS releases. Header still exposes legacy startup-plist management that overlaps with the newer privileged helper approach.

Test signals: enabling/disabling Kerberos login mechanism by OS version, backgrounder LaunchAgent creation/removal, `launchctl list` parsing, missing LaunchAgents directory, and authorization file backup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/PListManager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/PListManager.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/PListManager.m

Purpose: implements plist and launchd management for Kerberos-at-login, backgrounder activation, and legacy AFS startup plist handling.

Important APIs and control flow: `krb5TiketAtLoginTime:helper:` reads Active Directory prefs and skips changes when AD auth authority generation is enabled, reads `/etc/authorization`, locates `system.login.console` mechanisms, replaces the OS-version-specific mechanism with `builtin:krb5authnoverify,privileged` or restores it, serializes to `/tmp/authorization`, backs up `/etc/authorization`, chowns temp file to root:wheel, and moves it into `/etc`. `installBackgrounderLaunchdFile:` creates a per-user LaunchAgent plist for `AFSBackgrounder.app` or removes it. `launchctlCommand:` builds a user/system Library LaunchAgents path and runs `/bin/launchctl`. `launchdJobState:` runs `launchctl list jobName`.

State and persistence: mutates `/etc/authorization`, `/etc/authorization_bk`, `~/Library/LaunchAgents/it.infn.lnf.network.AFSBackgrounder.plist`, and launchd job state.

Dependencies and integration: `AFSCommanderPref` calls these methods for UI toggles. `FileUtil` performs privileged `/etc/authorization` updates; `TaskUtil` runs unprivileged launchctl/mv/rm calls.

Risks: `indexOfObject:` returning `NSNotFound` is not checked before `replaceObjectAtIndex:`. Editing `/etc/authorization` is fragile and obsolete on modern macOS. Some temp moves use unprivileged `mv`. The `helper` argument is unused in the visible implementation. `launchctlCommand` always constructs `LaunchAgents`, even for non-user domains.

Test signals: OS 10.4/10.5/10.6 mechanism replacement, missing target mechanism, malformed plist, AD skip condition, LaunchAgents directory missing, backgrounder path correctness, launchctl load/unload arguments, and job-state false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/PListManager.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/SystemUIPlugin.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/SystemUIPlugin.h

Purpose: declares private AppKit/SystemUIServer interfaces for menu extras, dock extras, and menu-extra views used by legacy menu bar integration.

Important APIs and types: defines `NSMenuExtra`, `NSMenuExtraPrivate`, `NSDockExtra`, dock/menu item helper categories, `NSApplicationDockExtra`, and `NSMenuExtraView` method surfaces. Methods cover initialization with bundles/data, image/menu/title/action/target properties, popup/unload behavior, accessibility attributes, dock menu commands, and menu item dictionary helpers.

Control flow and persistence: header only. It enables code to compile against private system classes without official SDK headers.

Dependencies and integration: imports AppKit. Related to the background menu extra and comments in `AFSCommanderPref.h` about loading/unloading menu extras.

Risks: these are private APIs and can break across macOS releases or cause App Store/signing rejection. Many methods use untyped `id` and historical parameter names. Accessibility and UI behavior depend on private implementation details.

Test signals: compile against the target SDK, runtime class availability, menu extra load/unload on supported macOS versions, and fallback behavior when private APIs are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/SystemUIPlugin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TaskUtil.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TaskUtil.h

Purpose: declares shell-command and privileged-helper utilities used by preference pane controllers and configuration managers.

Important APIs and constants: `PRIVHELPER_ID` is `org.openafs.privhelper`. Methods search executable paths, run commands via `NSTask`, send generic privileged tasks, and send backup/write privileged tasks with filenames/data.

Control flow and persistence: unprivileged commands return captured stdout as strings. Privileged commands are sent to the XPC Mach service implemented by `PrivilegedHelper/privhelper.c.in`; persistent effects depend on the requested helper task.

Dependencies and integration: imports Cocoa and Security Authorization headers. `AFSPropertyManager`, `AFSCommanderPref`, and `PListManager` use it heavily.

Risks: filename/data are exposed as `char *` in the generic API even though wrapper methods pass UTF-8 strings. Callers must use exact task names recognized by the helper.

Test signals: command path lookup, stdout trimming, nonzero exit behavior, helper unavailable, denied authorization, backup/write allowed paths, and start/stop/startup task names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TaskUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TaskUtil.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TaskUtil.m

Purpose: implements command execution and XPC privileged-helper RPC.

Important APIs and control flow: `executeTaskSearchingPath:args:` resolves a command with `/usr/bin/which` and executes it. `executeTask:arguments:` launches an `NSTask`, sets a custom PATH, captures stdout, trims the final byte, and returns nil on nonzero status. `executePrivTask:filename:data:` obtains authorization through `AuthUtil`, serializes `AuthorizationExternalForm`, creates a privileged Mach service XPC connection to `org.openafs.privhelper`, sends `task`, `auth`, optional `filename`, and optional `data`, waits synchronously, and extracts integer `status`. Wrapper methods implement no-arg tasks, backup, and write.

State and persistence: no local persistent state. Privileged helper requests affect launchd state, AFS service state, or config files under `/var/db/openafs`.

Dependencies and integration: depends on ServiceManagement, Security, XPC, and `AuthUtil`. Called from the preference pane and property manager.

Risks: synchronous XPC calls can block the UI. `executeTask:` trims one byte from all nonempty stdout, which can corrupt output that lacks a trailing newline. The PATH string includes literal `$PATH`, not expansion. It does not capture stderr. Helper errors are returned but many callers ignore nonzero statuses.

Test signals: stdout with and without trailing newline, stderr-only failures, nonexistent commands, PATH lookup for OpenAFS tools, helper not installed, invalid reply type, denied authorization, and each helper task status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TaskUtil.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TestLib.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TestLib.m

Purpose: scratch/test harness source for manually exercising preference-pane code and UI alert behavior.

Important APIs and control flow: imports `AFSPropertyManager`, `FileUtil`, `TaskUtil`, and `global.h`; declares CoreMenuExtra symbols; `main` creates an autorelease pool and shows a simple `NSAlert`. Commented lines show previous manual tests for loading/saving AFS configuration and `aklog`. `printNSArray` logs object descriptions.

State and persistence: as currently active, only displays an alert and has no persistent effect. Uncommented test lines could modify AFS configuration via `AFSPropertyManager`.

Dependencies and integration: links against Cocoa/Foundation and local preference-pane classes. Not part of the core runtime unless explicitly built.

Risks: if built or run with commented code restored, it can write real OpenAFS configuration. It contains no automated assertions and no exit-status validation.

Test signals: treat as manual-only; useful scenarios are configuration load/save smoke tests, alert display, and array logging, but proper tests should mock `TaskUtil` and temporary config trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TestLib.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TokenCredentialController.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TokenCredentialController.h

Purpose: declares the modal credential sheet controller used when the user obtains AFS tokens with klog instead of aklog.

Important APIs and state: stores `credentialPanel`, parent/controller references, username and password text fields, `taken`, `uName`, and `uPwd`. Exposes `getToken:`, `closePanel:`, `takenToken`, `uName`, and `uPwd`.

Control flow and persistence: credentials are in-memory only. `AFSCommanderPref didEndCredentialSheet:` reads them and calls `AFSPropertyManager getTokens:true usr:pwd:`.

Dependencies and integration: imports Cocoa. It is loaded from `CredentialPanel` nib by the main preference pane.

Risks: password is retained in an NSString and not cleared. Empty string detection in implementation uses pointer equality. Outlets are untyped `id`.

Test signals: empty fields, successful submit, cancel, password lifetime after sheet close, and parent token-acquisition call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TokenCredentialController.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TokenCredentialController.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TokenCredentialController.m

Purpose: implements the username/password sheet for klog token acquisition.

Important APIs and control flow: `getToken:` reads the username and password text fields into `uName` and `uPwd`, returns early if either is pointer-equal to `@""`, sets `taken = YES`, and ends the sheet. `closePanel:` sets `taken = NO` and ends the sheet. Accessors return the taken flag and credential strings.

State and persistence: credential strings are kept only in controller ivars, then passed to `AFSPropertyManager`. They are not written to preferences.

Dependencies and integration: loaded by `AFSCommanderPref getNewToken:` when aklog is disabled. Imports `TaskUtil` but does not use it directly.

Risks: string pointer comparison is incorrect for empty validation. Password remains as an immutable Objective-C string until overwritten/released. `taken` is not reset in `awakeFromNib`, so reused controller state could matter.

Test signals: empty field validation with distinct empty NSString instances, cancel after previous successful submit, secure text field behavior, and downstream klog invocation arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TokenCredentialController.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/afshlp.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/afshlp.m

Purpose: tiny setuid-style exec helper.

Important APIs and control flow: `main` reads the effective uid, calls `setuid(euid)`, and then `execve(argv[1], &argv[1], envp)`. It returns `-1` if `setuid` fails.

State and persistence: no persistent state. It transforms process credentials and executes the requested program.

Dependencies and integration: used by `AFSCommanderPref krb5KredentialAtLoginTimeEvent:` as the helper path passed to `PListManager krb5TiketAtLoginTime:helper:`, though the visible plist manager implementation does not use that argument.

Risks: no argument-count check before `argv[1]`. If installed setuid, it is a broad exec primitive for any supplied path and arguments. Error reporting from `execve` failure is absent.

Test signals: invocation with no argv[1], valid target execution, environment preservation, setuid failure, and installed permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/afshlp.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/global.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/global.h

Purpose: central macro header for preference-pane localized strings, preference keys, bundle identifiers, menu/backgrounder paths, notification names, and timing constants.

Important APIs and state: defines `TOKENS_REFRESH_TIME_IN_SEC`, localized string macros for UI labels/errors, `PREFERENCE_*` keys for CFPreferences, default Kerberos renewal values, static AFS config base `/var/db/openafs`, menu extra resource URLs, backgrounder and preference bundle IDs, and distributed notification object/name constants.

Control flow and persistence: not executable, but its keys define persistent CFPreferences storage and interprocess notification contracts between `AFSCommanderPref` and `AFSBackgrounder`.

Dependencies and integration: consumed throughout the preference pane, link creation, PListManager flows, and backgrounder-related code.

Risks: macros reference `self` and `[self bundle]`, so they are only safe in Objective-C instance-method contexts. Notification constants include duplicate values (`kMExtraClosedNotification` and `kPrefChangeNotification`) that can blur event semantics. The static config path must match the privileged helper prefix.

Test signals: preference key round trips, localization table coverage, distributed notification delivery, backgrounder resource lookup, and consistency between config path macros and helper paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/portability.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/portability.h

Purpose: compatibility shim for pre-Leopard SDKs that may not define `NSInteger` and `NSUInteger`.

Important APIs and state: when `NSINTEGER_DEFINED` is absent, defines `NSInteger` and `NSUInteger` as long/unsigned long for 64-like builds or int/unsigned int otherwise, then defines min/max constants and marks `NSINTEGER_DEFINED`.

Control flow and persistence: header-only compile-time compatibility, no runtime state.

Dependencies and integration: included by `PListManager.m` and potentially other legacy Objective-C sources.

Risks: typedefs can conflict if included after newer Foundation headers with different definitions. Uses `LONG_MAX`, `LONG_MIN`, and `ULONG_MAX` without including limits here, relying on transitive includes.

Test signals: compile on old and new SDKs, 32-bit and 64-bit targets, include order with Cocoa/Foundation, and warnings about duplicate typedefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/portability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AklogAuthPlugin/aklog.c -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AklogAuthPlugin/aklog.c

Purpose: Authorization Services plugin mechanism that runs `aklog` during login so users get AFS tokens after authentication.

Important APIs and control flow: defines `PluginRef` with callbacks and `MechanismRef` with plugin, engine, and mechanism argument. `AuthorizationPluginCreate` returns `pluginInterface`. `mechanismCreate` stores the mechanism id string as an optional cell argument. `mechanismInvoke` calls `invokeAklog`. `invokeAklog` reads `kDS1AttrUniqueID` and `kDS1AttrPrimaryGroupID` from the authorization context, temporarily switches credentials with `pthread_setugid_np`, runs `do_aklog`, restores uid/gid, and sets authorization result allow. `do_aklog` uses `system("/usr/bin/aklog ...")`.

State and persistence: no persistent state. Runtime state is one mechanism instance per login mechanism invocation.

Dependencies and integration: uses Security AuthorizationPlugin APIs, DirectoryService attribute keys, syslog, `pthread_setugid_np`, and `/usr/bin/aklog`. Built as `aklog.bundle` by the Darwin Makefile/Xcode project.

Risks: `system()` with a mechanism-supplied cell string is command-injection sensitive. Fixed `/usr/bin/aklog` may not match install paths. Failure returns internal authorization errors that can affect login. The code comments note a desired future `libaklog` replacement.

Test signals: plugin load/unload, context values present/missing, uid/gid switch success/failure, default and cell-specific mechanisms, aklog failure behavior, and injection-resistant handling of mechanism arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AklogAuthPlugin/aklog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/Makefile.in -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/Makefile.in

Purpose: top-level Darwin platform build/install makefile for OpenAFS macOS UI/helper artifacts.

Important targets and control flow: `all` builds `OpenAFS.prefPane`, `afssettings`, `afscell`, `growlagent`, `aklog.bundle`, and `PrivilegedHelper`. Xcode projects build the preference pane, auth plugin, and installer pane. `afssettings` is compiled directly with Foundation. `growlagent` and `PrivilegedHelper` delegate to subdirectory makefiles. `dest` copies bundle outputs into `${DEST}/tools` and `${DEST}/installer`; `install` installs runtime command/helper components.

State and persistence: build outputs are under per-project `build` directories plus `afssettings`. Destination paths populate packaging trees and `${sbindir}`.

Dependencies and integration: includes OpenAFS config makefiles and pthread flags. Uses `xcodebuild`, compiler variables, `INSTALL`, and recursive make.

Risks: build depends on Xcode project files and legacy target names. `clean` removes broad build directories. Bundle copy targets use `rm -rf` on destination bundle paths.

Test signals: out-of-tree build, `DEST` package staging, `DESTDIR` install, clean idempotence, Xcode build flags propagation, and presence of all expected bundle artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/Makefile.in -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/Makefile.in

Purpose: builds and stages the `org.openafs.privhelper` privileged XPC helper embedded in the preference pane bundle.

Important targets and control flow: `all` builds `org.openafs.privhelper` from generated `privhelper.c`, using `AFS_LDRULE`, minimum macOS 10.6, embedded `__info_plist` from `privhelper-info.plist`, embedded `__launchd_plist` from `privhelper-launchd.plist`, and Security/CoreFoundation frameworks. `dest` installs the helper under `OpenAFS.prefPane/Contents/Library/LaunchServices`.

State and persistence: build output is the helper executable. Staging path is inside the preference pane so ServiceManagement can bless/install it.

Dependencies and integration: includes OpenAFS config and version makefiles. Must match `Info.plist.in` `SMPrivilegedExecutables` and `TaskUtil` service id.

Risks: embedded plist section paths must exist at link time. Code signing/blessing fails if the helper is not staged exactly where ServiceManagement expects. `install` target is empty; packaging relies on `dest`.

Test signals: helper links with embedded plist sections, staged bundle path correctness, code signing requirements, and ServiceManagement installation from the preference pane.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/privhelper-info.plist.in -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/privhelper-info.plist.in

Purpose: Info.plist template embedded in the privileged helper executable.

Important keys: `CFBundleIdentifier` is `org.openafs.privhelper`, version metadata is static, and `SMAuthorizedClients` restricts clients to the signed preference pane identifier `it.infn.lnf.network.openafs` with Apple generic/Developer ID certificate constraints and `@MACOS_TEAM_ID@`.

State and persistence: build-time metadata used by ServiceManagement and launchd when blessing or validating the helper.

Dependencies and integration: must align with `TaskUtil`'s service name, `AFSPreference/Info.plist.in` `SMPrivilegedExecutables`, and the runtime code-signing checks inside `privhelper.c.in`.

Risks: Team ID substitution or bundle identifier mismatch prevents helper installation or client authorization. The runtime helper also allows backgrounder/menu identifiers, so plist authorized clients and runtime code requirements must be reviewed together.

Test signals: validate substituted plist, code-signing requirement syntax, SMJobBless acceptance, and client connection from the signed preference pane.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/privhelper-info.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/privhelper.c.in -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/privhelper.c.in

Purpose: implements the root privileged XPC helper for the macOS preference pane and backgrounder.

Important APIs and control flow: `main` creates a Mach service listener for `org.openafs.privhelper`, installs code-signing requirements, and dispatches incoming connections. `XPCEventHandler` rejects unauthorized connections, rejects missing/invalid external authorization, extracts `task`, calls `ProcessRequest`, and replies with integer `status`. `IsConnAuthorized` uses `xpc_connection_set_peer_code_signing_requirement` on newer SDKs or `SecCodeCreateWithXPCMessage`/`SecCodeCheckValidity` on older SDKs. `IsEventAuthorized` deserializes `AuthorizationExternalForm` and verifies `kAuthorizationRightExecute`. `ProcessRequest` implements `startup_enable`, `startup_disable`, `startup_check`, `afsd_start`, `afsd_stop`, `backup`, and `write`.

State and persistence: persistent effects include `launchctl load/unload -w /Library/LaunchDaemons/org.openafs.filesystems.afs.plist`, running `/Library/OpenAFS/Tools/root.client/usr/vice/etc/afs.rc start|stop`, copying config backups, and writing allowlisted files under `/var/db/openafs`. `WriteFile` writes a temp file, chowns root:wheel, then atomically moves it into place.

Dependencies and integration: receives messages from `TaskUtil.m`. Code requirements include Apple System Preferences legacy loaders and signed OpenAFS identifiers. Uses XPC, Security.framework, CoreFoundation, syslog, `posix_spawn`, and `waitpid`.

Risks: the allowlist must stay synchronized with UI write targets. `RunCommand` passes at most four argv entries and uses inherited environment. `WriteFile` writes string data, so embedded NUL bytes are unsupported. Code-signing requirement changes across macOS versions are complex. Unknown tasks return `-1`, but callers often only log or ignore status.

Test signals: authorized and unauthorized client connections, invalid external auth data, each fixed task path, allowlist rejection, backup no-clobber semantics, write temp/chown/move failure, launchctl status interpretation, older SDK code-signing fallback, and helper response format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/privhelper.c.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/afscell/afscellPane.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/afscell/afscellPane.h

Purpose: declares an Installer.app plugin pane for configuring the local AFS cell and optional alias during installation.

Important APIs and state: `afscellPane` subclasses `InstallerPane` and has outlets for `ThisCell` and `CellAlias` text fields. The implementation overrides pane title, entry, and exit behavior.

Control flow and persistence: no methods are declared in the header beyond inherited installer lifecycle. The implementation reads current config and writes temporary installer handoff files.

Dependencies and integration: imports Cocoa and `InstallerPlugins/InstallerPlugins.h`. Built as `afscell.bundle` by the Darwin Makefile.

Risks: depends on Apple's legacy Installer plugin API. The header's untyped outlets provide no compile-time binding checks.

Test signals: bundle load in Installer, text field outlet wiring, pane title localization, and installer forward/back navigation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/afscell/afscellPane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/afscell/afscellPane.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/afscell/afscellPane.m

Purpose: implements the installer pane that reads existing local cell settings and writes user-selected `ThisCell`/`CellAlias` values for the installer to consume.

Important APIs and control flow: helper methods validate word/cell/alias syntax, parse a `CellAlias` line for the current cell, append old or new alias lines, and show alert panels. `didEnterPane:` reads `/private/var/db/openafs/etc/ThisCell` and `CellAlias`, displays the first local cell line, and finds its alias. `shouldExitPane:` on forward navigation validates the cell, writes `/private/tmp/org.OpenAFS.Install.ThisCell.<username>`, optionally validates alias, rewrites or appends a matching alias line, and writes `/private/tmp/org.OpenAFS.Install.CellAlias.<username>`.

State and persistence: persistent existing config is read from `/private/var/db/openafs/etc`. New installer data is written to user-suffixed temp files under `/private/tmp`, not directly into final config.

Dependencies and integration: InstallerPane lifecycle, Cocoa scanners/alerts, and later installer scripts that consume the temp files.

Risks: username in temp filename is not sanitized. Alias parsing is scanner-based and may mishandle comments/whitespace. Alerts allow continuing after write failures, which can produce partial installer state. The validation only allows alphanumeric and hyphen labels, with dots for cells.

Test signals: no existing ThisCell, no CellAlias, valid and invalid domain-style cells, empty cell continue/cancel, alias replace/append/no-op, temp-file write failure, and usernames with unusual characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/afscell/afscellPane.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/afssettings.m -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/afssettings.m

Purpose: command-line tool that reads OpenAFS Darwin settings from a plist and applies them to the AFS kernel filesystem via sysctl.

Important APIs and control flow: `mygetvfsbyname` discovers the VFS type number for `afs` and seeds the sysctl OID. `recurse` walks a tree of `Setting` descriptors and plist dictionaries; leaf numeric values are written with `sysctl`, and leaf strings are written as UTF-8 bytes. Static setting trees map `All/RealModes`, `All/FSEvents`, `All/Bulkstat`, and Darwin-version nodes to `AFS_SC_*` selectors. `main` loads `/var/db/openafs/etc/config/settings.plist`, parses it as a property list, and recurses into the sysctl tree.

State and persistence: input is persistent plist configuration; output mutates live kernel/sysctl state for the AFS filesystem. It does not write the plist.

Dependencies and integration: includes `<afs/sysctl.h>`, Foundation/CoreFoundation, BSD `sysctl`, and mount/VFS structures. Built and installed by `DARWIN/Makefile.in`.

Risks: setting descriptors with `Node` and no children are skipped, so Darwin-version-specific empty nodes are placeholders. Invalid plist value types can be sent to numeric/string sysctl leaves. Errors are printed to stderr but processing continues. Requires AFS VFS to be present.

Test signals: missing AFS filesystem, missing/malformed settings plist, numeric and string sysctl success/failure, unknown keys ignored, nested `All/Darwin` settings, and errno reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/afssettings.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlDefines.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlDefines.h

Purpose: bundled Growl public constants header defining registration, notification, and distributed-notification keys used by Growl clients or the local Growl agent.

Important APIs and state: `XSTR`/`STRING_TYPE` bridge Objective-C and CoreFoundation builds. Defines keys such as `GROWL_APP_NAME`, `GROWL_APP_ID`, app icon, default/all notifications, human-readable names, notification title/description/icon/priority/sticky/click context/display plugin/identifier/progress, and distributed notification names for registration, notification, shutdown, ping/pong, readiness, clicked, and timed out events.

Control flow and persistence: header-only constants. UserInfo dictionaries built with these keys flow through distributed notifications or Growl framework compatibility paths.

Dependencies and integration: used by `growlagent` code and any OpenAFS component that posts Growl notifications. Compatible with ObjC and C/CF consumers.

Risks: Growl direct distributed notifications are documented in this header as deprecated in favor of Growl.framework delegate APIs. String constants are legacy and must match the installed Growl version. No runtime validation of dictionary value types.

Test signals: registration dictionary acceptance by Growl, notification delivery with required keys, optional icon/progress/sticky handling, click callback context, and ObjC vs C macro expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlDefines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlDefinesInternal.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlDefinesInternal.h

Purpose: bundled Growl internal constants/types for network notification packets, plugin preferences, compatibility typedefs, and preference update macros.

Important APIs and state: defines fallback `NSInteger`, `NSUInteger`, and `CGFloat`, Growl network TCP/UDP ports, protocol versions, packet type constants, packed `GrowlNetworkPacket`, `GrowlNetworkRegistration`, and `GrowlNetworkNotification` structs, preference keys for Growl enabled/screenshot/app location/remote address, bundle identifiers and plugin extensions, and macros to synchronize/update/read/write Growl helper app preferences.

Control flow and persistence: preference macros read/write nested plugin settings inside the `com.Growl.GrowlHelperApp` preference domain and post `GrowlPreferencesChanged`. Packet structs define serialized network protocol layout.

Dependencies and integration: includes CoreFoundation, sys/types, and unistd. Used by Growl agent internals and plugin code compiled in this Darwin subtree.

Risks: packed bitfield layout in `GrowlNetworkNotificationFlags` is endian-sensitive. Preference macros rely on CoreFoundation ownership discipline and caller-provided domains/types. Legacy Growl ports and protocol versions may be incompatible with modern notification systems.

Test signals: struct sizes and byte order, registration/notification packet encode/decode, MD5/SHA256/no-auth type handling, preference read/write for bool/int/float/value, distributed preference update notification, and 32/64-bit CGFloat behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlDefinesInternal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlPathway.h -->
# Research: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlPathway.h

Purpose: declares the Growl pathway protocol and base class used for in-process or distributed Growl notification handling.

Important APIs and state: `GrowlNotificationProtocol` declares one-way `registerApplicationWithDictionary:` and `postNotificationWithDictionary:` plus `growlVersion`. `GrowlPathway` subclasses `NSObject` and conforms to the protocol without declaring ivars.

Control flow and persistence: header-only contract. Implementations receive registration dictionaries and notification dictionaries, then return version information.

Dependencies and integration: imports Foundation and references `GrowlApplicationController`. Used by Growl agent components under the Darwin platform tree.

Risks: the protocol uses Distributed Objects-style `oneway` and `bycopy` annotations, which are legacy and constrain object serialization to property-list-like dictionaries. The header alone does not validate required Growl keys.

Test signals: protocol conformance in implementation classes, distributed object invocation, dictionary copy semantics, registration followed by notification, and version string compatibility with Growl clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlPathway.h -->
