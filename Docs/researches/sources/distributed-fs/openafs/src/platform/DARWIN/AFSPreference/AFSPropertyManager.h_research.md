# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSPropertyManager.h

Purpose: declares the model/service object used by the preference pane to read, mutate, and persist OpenAFS client configuration, daemon state, CellServDB entries, cache manager parameters, and token operations.

Important APIs and types: `AFSPropertyManager` stores `installationPath`, default cell name, mutable `cellList`, user token-default cells, cacheinfo fields, afsd option flags, `FileUtil`, and `useAfsdConfVersion`. Public methods cover initialization, getters/setters for cache manager knobs, `loadConfiguration`, `clearConfiguration`, `readCellInfo`, `readCellDB`, `readTheseCell`, `saveConfigurationFiles:`, `saveCacheConfigurationFiles:`, `startup`, `shutdown`, `checkAfsStatus`, `getTokenList`, `klog`, `aklog`, `getTokens`, `unlog`, and `makeChaceParamString`.

State and persistence: constants identify legacy startup scripts, launchd plist names, AFS mount strings, `/var/db/openafs` as the default base, old `afsd.options`, new `afs.conf`, `cacheinfo`, `ThisCell`, `CellServDB`, and `TheseCells`. The header is the contract between UI controllers and the privileged helper path.

Dependencies and integration: imports `DBCellElement` for CellServDB rows and `FileUtil` for older Authorization Services file operations. The implementation additionally integrates `TaskUtil` and Kerberos helpers.

Risks: method comments document old and new config formats, but no validation contract is exposed for numeric ranges or path safety. Header names contain typos (`makeChaceParamString`) that are ABI/API visible. Consumers can mutate the returned `NSMutableArray *` directly.

Test signals: compile all declarations against callers, verify old/new afsd option selection by OpenAFS version, cover direct mutation of `getCellList`, and check that all privileged write callers use only paths accepted by the helper allowlist.
