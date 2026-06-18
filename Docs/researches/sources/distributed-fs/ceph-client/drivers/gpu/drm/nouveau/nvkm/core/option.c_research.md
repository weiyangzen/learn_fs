## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/option.c

### Purpose
`option.c` parses Nouveau's comma-separated configuration and debug option strings. It provides string, boolean, numeric, and debug-level extraction for module and per-subdevice configuration.

### Important APIs, types, and functions
The exported helpers are `nvkm_stropt()`, `nvkm_boolopt()`, `nvkm_longopt()`, and `nvkm_dbgopt()`. Debug parsing maps textual levels to `NV_DBG_FATAL`, `NV_DBG_ERROR`, `NV_DBG_WARN`, `NV_DBG_INFO`, `NV_DBG_DEBUG`, `NV_DBG_TRACE`, `NV_DBG_PARANOIA`, and `NV_DBG_SPAM`.

### Control flow
`nvkm_stropt()` scans `name=value` pairs separated by commas or equal signs and returns the value span plus length for a matching option. `nvkm_boolopt()` uses that span to accept common true/false words while preserving the supplied default on unknown values. `nvkm_longopt()` duplicates the value substring, parses it with `kstrtol(..., base 0)`, and preserves the default on parse failure. `nvkm_dbgopt()` scans a debug string with optional `subsystem=level` scoping and returns the current default level after applying matching tokens.

### State and persistence behavior
The file is stateless. It reads immutable option strings and returns parsed values. `nvkm_longopt()` allocates a temporary copy of a value and frees it before returning.

### Dependencies
It depends on `core/option.h`, `core/debug.h`, kernel string helpers, `kstrndup()`, `kstrtol()`, and `CONFIG_NOUVEAU_DEBUG_DEFAULT`.

### Integration points
Device construction uses `nvkm_longopt()` for development chipset override and `nvkm_boolopt()` for unsupported-chipset enabling. Subdevice construction uses `nvkm_dbgopt()` to set per-subdevice log verbosity. Other Nouveau components use these helpers for module option parsing without duplicating scanner logic.

### Risks
The scanner is simple and treats comma/equal delimiters specially; option values cannot contain those characters. Unknown boolean strings silently keep the old value. Debug parsing has a mode flag that changes after scoped entries, so malformed strings can broaden or narrow the effect of later tokens.

### Test signals
Useful tests cover empty strings, missing values, repeated options, mixed case names and values, scoped debug strings, numeric bases accepted by `kstrtol`, and malformed option strings that should leave defaults intact.
