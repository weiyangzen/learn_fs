# sources/distributed-fs/openafs/src/WINNT/talocale/tal_main.cpp

## Purpose

`tal_main.cpp` implements TaLocale's core resource-location service. It maintains a priority-ordered module list, initializes default language selection, loads locale-specific resource DLLs, supports a registry language override, and wraps Win32 resource loading for dialogs, string tables, menus, images, icons, and accelerators.

## Important APIs, Types, and Functions

- `MODULE` stores a search priority and `HINSTANCE`.
- Static state includes `l_lang`, `l_csModules`, `l_aModules`, and `l_cModules`.
- `TaLocale_Initialize()` initializes common controls, the module-list critical section, default executable module, user default language, and optional registry override.
- `TaLocaleReallocFunction()` backs the public `REALLOC` macro using TaLocale allocation functions.
- `TaLocale_GuessBestLangID()` maps broad locales to likely shipped sublanguages such as US English, Simplified Chinese, German, Spanish, and Brazilian Portuguese.
- `TaLocale_SpecifyModule()` adds, reorders, or removes modules in priority order.
- `FindAfsCommonPathByComponent()` and `FindAfsCommonPath()` locate an AFS `Common` directory using Transarc/OpenAFS registry component paths.
- `TaLocale_LoadCorrespondingModule()` and `TaLocale_LoadCorrespondingModuleByName()` search for locale-suffixed DLLs such as `module_1033.dll`, wildcard language DLLs, AFS Common DLLs, and US-English fallback DLLs.
- `TaLocale_EnumModule()` enumerates the current module search chain.
- `TaLocale_GetLanguage()`, `TaLocale_SetLanguage()`, `TaLocale_GetLanguageOverride()`, `TaLocale_SetLanguageOverride()`, and `TaLocale_RemoveLanguageOverride()` manage volatile and registry language selection.
- `TaLocale_GetResource()`, `TaLocale_GetStringResource()`, `TaLocale_GetDialogResource()`, `TaLocale_LoadMenu()`, `TaLocale_LoadImage()`, `TaLocale_LoadIcon()`, and `TaLocale_LoadAccelerators()` are the resource-loading API.

## Control Flow

Most public entry points call `TaLocale_Initialize()` either directly or indirectly. Initialization uses a per-process-name mutex to avoid concurrent first-time initialization, initializes common controls and the module critical section, registers the executable module, sets `l_lang` from `GetUserDefaultLCID()`, then applies a persistent override if present.

Module registration removes any existing matching handle, then inserts the handle before lower-priority modules, growing the module array with `REALLOC`. Locale-DLL loading derives a filename from the supplied module or filename, replaces the extension with a language suffix, tries exact language, guessed language, wildcard language, AFS Common wildcard, and US-English fallback, then registers the loaded DLL at the requested priority.

Resource lookup iterates `TaLocale_EnumModule()` in priority order. General resources try `FindResourceEx()` for the selected language, US English, then any resource. String lookup computes the 16-string resource table and index, loads the table, walks length-prefixed entries, validates the selected string, and returns a pointer to the in-memory resource.

## State and Persistence

The module list and selected language are process-local static state protected by `l_csModules` for module operations. The language override is persisted under `HKLM\Software\Microsoft\Windows\CurrentVersion\Nls`, value `Default Language`. Loaded resource DLLs remain loaded for process lifetime unless managed elsewhere.

## Dependencies and Integration Points

The module depends on Win32 resource APIs, common controls, registry APIs, locale APIs, file search/loading APIs, and TaLocale string helpers (`FindBaseFileName`, `FindExtension`) plus allocation macros. It is the backend for `tal_string.cpp` and `tal_dialog.cpp`.

## Risks and Edge Cases

- `TaLocale_Initialize()` uses a non-interlocked static boolean plus a named mutex; recursive calls during initialization can be subtle because `TaLocale_SpecifyModule()` calls back into initialization.
- The module-array insertion loop casts `size_t` to `LONG` for reverse iteration, which is fragile for very large arrays.
- `TaLocale_GetResourceEx()` accepts `fSearchDefaultLanguageToo` but does not use it.
- `FindFirstFile()` is checked against `NULL`; Win32 returns `INVALID_HANDLE_VALUE`, so wildcard failure handling may be incorrect.
- String table walking uses exception handling around raw resource memory, which masks malformed resources but is not portable.
- Registry writes under HKLM require elevated privilege.

## Test Signals

Strong tests cover exact-language DLL loading, guessed-language fallback, wildcard/Common-directory fallback, module priority ordering, language override persistence/removal, string table lookup across missing entries, dialog/menu/image/accelerator lookup, and behavior when resource DLLs are absent.
