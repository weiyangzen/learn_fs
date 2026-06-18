# subset-b-009188 research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sl.json -->
## sources/sync-backup/syncthing/gui/default/assets/lang/lang-sl.json

### Purpose
`lang-sl.json` is the Slovenian translation catalog for the Syncthing default web GUI. It maps English UI message IDs to Slovenian display strings consumed by AngularJS `translate` directives, the `translate` filter, and `$translate.instant(...)` calls throughout `gui/default`.

### APIs, types, and data shape
This file exports no code symbols. Its API is a flat JSON object whose keys are canonical English message IDs and whose values are translated strings. Interpolation placeholders appear in keys as `{%name%}` style tokens and in values as Angular interpolation tokens such as `{{name}}`; the parsed catalog contains 460 keys against 558 English base keys, about 82.4% coverage. There are no extra keys, no empty translations, and no placeholder-token mismatches in the parsed data.

### Control flow
At runtime the GUI language path is selected by `LocaleService.useLocale(language, save2Storage)`, which delegates to `$translate.use(language)`. Once loaded, Angular's translate directive/filter resolves literal text from templates and controller strings against this JSON table. Missing Slovenian keys fall back through the translation subsystem rather than through logic in this file.

### State and persistence
The JSON file is static build-time data. It does not persist user state. The selected locale is persisted separately in browser `localStorage` under `SYN_LANG` by `LocaleService`, and the active document language is reflected through `document.documentElement.lang`.

### Dependencies and integration points
The file depends on the English source keys remaining stable and on Angular Translate's interpolation behavior. `valid-langs.js` includes `sl`, so this locale is expected to be selectable in the language menu. The adjacent `README.txt` states these language files are generated from Weblate and should not be hand-edited directly.

### Risks
The main risk is incomplete catalog coverage: 98 English keys are missing, including newer filtering, connection-management, block-indexing, authentication, and debug/status labels. A GUI path that reaches those strings will display fallback English. Some translated values include trailing spaces or wording issues, but structurally the catalog is parseable and interpolation-safe.

### Test signals
Useful checks are `jq empty lang-sl.json`, key-diff coverage against `lang-en.json`, placeholder set comparison between each key and translated value, and a GUI smoke test selecting Slovenian from the language menu and opening device, folder, settings, log, and notification dialogs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sl.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sq.json -->
## sources/sync-backup/syncthing/gui/default/assets/lang/lang-sq.json

### Purpose
`lang-sq.json` is the Albanian translation catalog for the Syncthing default web GUI. It provides a small set of English-to-Albanian UI strings for common navigation, action, device, folder, and status labels.

### APIs, types, and data shape
The file is a flat JSON object used as a data module by Angular Translate. It exports no functions, classes, or runtime types. The parsed catalog has 69 keys against the 558-key English base, about 12.4% coverage. It has no extra keys, no empty values, and no interpolation-token mismatches; the only value equal to its English key is `LDAP`, which is expected for an acronym.

### Control flow
If the Albanian locale is made available, `$translate.use('sq')` would load this table and translate only the keys present here. Angular templates and controller calls continue to request English message IDs as lookup keys. Any missing Albanian entry falls back to the translation library behavior.

### State and persistence
This catalog is immutable client-side data. It does not modify application settings or persisted configuration. Locale choice persistence is handled outside the file by `LocaleService` using the `SYN_LANG` localStorage key.

### Dependencies and integration points
The catalog depends on English message IDs from `lang-en.json`, Angular Translate, and Syncthing's generated language asset pipeline. `valid-langs.js` does not list `sq`, so the file may exist in the tree without being offered by the default GUI language selector unless the language list is regenerated elsewhere.

### Risks
Coverage is very sparse: 489 base keys are missing, so most GUI screens would remain in fallback English. Because the file has no interpolation examples, future additions with placeholders need explicit placeholder parity checks. Direct edits are risky because the directory README says Weblate is the authoritative source.

### Test signals
Run JSON parse validation, compare keys against `lang-en.json`, and confirm whether `sq` appears in generated available locales. If enabled manually, smoke-test basic navigation and verify fallback behavior is acceptable on screens with missing strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sq.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sr.json -->
## sources/sync-backup/syncthing/gui/default/assets/lang/lang-sr.json

### Purpose
`lang-sr.json` is the Serbian translation catalog for the Syncthing default web GUI. It currently covers only the beginning of the message catalog, mostly early alphabetic keys around device, address, add, network, and anonymous usage reporting copy.

### APIs, types, and data shape
This is a flat JSON object with English message IDs as keys and Serbian Cyrillic strings as values. It has no executable API. The parsed catalog contains 34 keys against 558 English keys, about 6.1% coverage. There are no extra keys, no empty values, no values left equal to English, and no placeholder mismatches for the single placeholder-bearing entry present.

### Control flow
Angular Translate uses the selected locale table as a lookup map. When a template contains `translate` or code calls `$translate.instant(...)`, the English message ID is looked up in this object. Missing Serbian entries are not handled here and will fall through according to the global translation configuration.

### State and persistence
The file stores static localization data only. It has no state transitions and does not persist anything. User locale selection and persistence are handled by `LocaleService`, browser language detection through `/svc/lang`, and optional `SYN_LANG` storage.

### Dependencies and integration points
The catalog depends on the English key set, Angular Translate, and the Weblate-generated asset flow. `valid-langs.js` does not include `sr`, so this file is not currently advertised by the default language dropdown in the checked-in language list.

### Risks
The dominant risk is extremely low coverage: 524 base keys are missing, including common confirmation dialogs, settings, folder/device edit surfaces, status strings, and most newer features. Since it is not listed in `valid-langs.js`, there is also an integration risk where updates to this file do not affect the visible GUI without language-list regeneration.

### Test signals
Validate JSON syntax, diff keys against `lang-en.json`, check interpolation placeholder parity, and verify `sr` presence or absence in the generated available locale list. If the locale is enabled, test screens with both covered and uncovered strings to confirm fallback rendering.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sr.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sv.json -->
## sources/sync-backup/syncthing/gui/default/assets/lang/lang-sv.json

### Purpose
`lang-sv.json` is the Swedish translation catalog for the Syncthing default web GUI. It covers the full current English base catalog, including device/folder management, discovery and listener status, file versioning, ignore rules, authentication, sharing helpers, ownership and extended attributes, and connection transport labels.

### APIs, types, and data shape
The file is a flat JSON object consumed by Angular Translate. It has no functions or classes. The parsed catalog contains 558 keys, matching the 558-key English base exactly: no missing keys, no extra keys, no empty values, and no placeholder-token mismatches. Ten values are intentionally or plausibly identical to English, including acronyms and protocol labels such as `LDAP`, `QUIC LAN`, `TCP WAN`, `OK`, and `Version`.

### Control flow
When `LocaleService` selects Swedish, `$translate.use('sv')` activates this lookup table. Template `translate` attributes, translate filters, and controller calls resolve through this map, including dynamic strings using translated values with `{{...}}` interpolation placeholders.

### State and persistence
The catalog is static. Runtime state is limited to the translation service cache and the user-selected locale persisted separately through `SYN_LANG` in localStorage. This file does not affect Syncthing configuration or synchronization state.

### Dependencies and integration points
The file integrates with `valid-langs.js`, which includes `sv`, and with the global display-name table from `prettyprint.js` used by the language selector. It depends on Angular Translate and the generated Weblate catalog pipeline documented by the asset directory README.

### Risks
Structural risk is low because coverage and placeholders match the English base. Remaining risks are linguistic quality, strings that intentionally stay English, and generated-file drift if the English catalog changes without a corresponding Weblate update. Long Swedish text can still stress modal, table, or button layouts.

### Test signals
Run JSON parse, exact key-set equality with `lang-en.json`, placeholder parity, and UI smoke tests after selecting Swedish. Useful paths include settings, add/edit device, add/edit folder, receive-encrypted folder warnings, sharing by email/SMS, logs, and version restore dialogs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sv.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-th.json -->
## sources/sync-backup/syncthing/gui/default/assets/lang/lang-th.json

### Purpose
`lang-th.json` is the Thai translation catalog for the Syncthing default web GUI, but currently contains only one translated message: the duplicate-device-ID warning.

### APIs, types, and data shape
The file is a valid flat JSON object. It exports no executable API. The parsed catalog has 1 key against the 558-key English base, about 0.2% coverage. There are no extra keys, no empty values, and no placeholder mismatches.

### Control flow
If Thai were selected, Angular Translate would resolve only the one present message from this table. Every other translated template or controller string would be missing from this locale and would rely on the application translation fallback behavior.

### State and persistence
This is static localization data. Locale choice and persistence are managed elsewhere by `LocaleService`, including browser-language detection and optional storage in `SYN_LANG`.

### Dependencies and integration points
The catalog depends on English message IDs and Angular Translate. `valid-langs.js` does not include `th`, so this file is not currently selectable through the default checked-in language menu. The directory README says language assets are generated from Weblate, so translation changes should flow through that service.

### Risks
The practical risk is that the file gives the appearance of Thai support while providing almost no UI coverage. If enabled, nearly all screens would fall back to English. Because only one string is present, there is little current interpolation risk, but future placeholder-bearing translations must preserve token names.

### Test signals
Validate JSON syntax, diff against `lang-en.json`, and confirm Thai is intentionally excluded from `valid-langs.js`. If enabling Thai, require much broader coverage and GUI smoke tests before exposing it in the language selector.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-th.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-tr.json -->
## sources/sync-backup/syncthing/gui/default/assets/lang/lang-tr.json

### Purpose
`lang-tr.json` is the Turkish translation catalog for the Syncthing default web GUI. It covers the full English base catalog, including legacy GUI strings and newer features such as connection management, ownership, extended attributes, block indexing, sharing helpers, and authentication copy.

### APIs, types, and data shape
The file is a flat JSON object with 558 keys, exactly matching the 558-key English base. It exports no functions or classes. There are no missing keys, no extra keys, no empty values, and no placeholder-token mismatches. Five values remain identical to English, all acronym/protocol-style strings: `LDAP`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`.

### Control flow
When the selected locale is Turkish, `LocaleService.useLocale('tr', ...)` calls `$translate.use('tr')`. Angular Translate then uses this JSON table for `translate` directives, translate filters, and `$translate.instant(...)` controller calls. Dynamic values such as device names, folder labels, versions, URLs, and paths are injected through preserved interpolation placeholders.

### State and persistence
The catalog itself is read-only static data. It does not update Syncthing config or local runtime state. User language selection is persisted in `localStorage` by `LocaleService` under `SYN_LANG`, and the page `lang` attribute is updated outside this file.

### Dependencies and integration points
The file depends on Angular Translate, the English source key set, `valid-langs.js` including `tr`, and the Weblate-generated asset workflow. It is integrated into the language menu through Syncthing's locale service and display-name infrastructure.

### Risks
Structural risk is low because coverage is complete and placeholders match. The remaining risks are translation quality, text length in constrained controls, and future drift if English keys are added without regenerating the Turkish catalog. Generated-file status means local patches are likely overwritten by the translation import pipeline.

### Test signals
Run JSON parse, exact key-set equality against `lang-en.json`, placeholder parity checks, and Turkish GUI smoke tests across settings, device/folder editing, encrypted folder warnings, share-by-email/SMS flows, logs, and restore/version dialogs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-tr.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-uk.json -->
## sources/sync-backup/syncthing/gui/default/assets/lang/lang-uk.json

### Purpose
`lang-uk.json` is the Ukrainian translation catalog for the Syncthing default web GUI. It is nearly complete and covers most device, folder, synchronization, configuration, discovery, authentication, notification, and status surfaces.

### APIs, types, and data shape
The file is a flat JSON object consumed as a translation table. It exposes no executable API. The parsed catalog contains 551 keys against the 558-key English base, about 98.7% coverage. There are no extra keys, no empty values, and no placeholder-token mismatches. Five protocol/acronym values remain identical to English: `LDAP`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`.

### Control flow
When Ukrainian is selected, Angular Translate resolves English message IDs through this table. Strings are requested from templates through `translate` attributes and filters and from controllers through `$translate.instant(...)`. Missing entries fall through to global translation fallback behavior.

### State and persistence
This catalog contains no mutable application state. Locale persistence is handled by `LocaleService` with the `SYN_LANG` localStorage key. The file has no direct relation to Syncthing configuration, folder state, or sync metadata persistence.

### Dependencies and integration points
`valid-langs.js` includes `uk`, so this locale is exposed through the language selector. The catalog depends on the English base keys, Angular Translate interpolation, display names from `prettyprint.js`, and the Weblate generation process noted in the directory README.

### Risks
The main risk is a small set of missing newer keys: `Block Indexing`, `Device Group`, `Folder Group`, the long block-indexing description, optional group descriptions for device and folder, and `Starting`. These gaps affect newer configuration/status UI and will fall back to English. Layout risk also exists for longer Ukrainian labels in narrow controls.

### Test signals
Validate JSON syntax, run key-set diff against `lang-en.json`, verify placeholder parity, and smoke-test Ukrainian through the visible language menu. Include screens for grouped devices/folders, block indexing, startup/status display, and common device/folder dialogs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-uk.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-vi.json -->
## sources/sync-backup/syncthing/gui/default/assets/lang/lang-vi.json

### Purpose
`lang-vi.json` is the Vietnamese translation catalog for the Syncthing default web GUI. It covers about half of the current English catalog, with translations for many common device/folder actions, warnings, ignore patterns, file versioning concepts, and synchronization status labels.

### APIs, types, and data shape
The file is a flat JSON object and has no executable exports. The parsed catalog has 276 keys against the 558-key English base, about 49.5% coverage. It has no extra keys and no placeholder-token mismatches. Two values are empty strings, and two values match English exactly (`LDAP` and `OK`).

### Control flow
If Vietnamese is selected, Angular Translate looks up English message IDs in this table for directives, filters, and controller-generated labels. Present placeholder-bearing strings preserve the expected interpolation token names, so dynamic values such as device IDs, folder labels, paths, versions, and URLs can be inserted safely. Missing or empty entries rely on translation fallback behavior or may render as blank depending on Angular Translate handling for the exact path.

### State and persistence
This file is static localization data. It does not persist settings, sync state, or user choices. The selected locale is managed separately by `LocaleService`, including localStorage persistence under `SYN_LANG`.

### Dependencies and integration points
The catalog depends on Angular Translate and the English base key set. `valid-langs.js` does not include `vi`, so this file is not currently exposed in the default checked-in language selector. The directory README indicates the file is generated from Weblate rather than manually maintained.

### Risks
Coverage is partial, with 282 missing English keys across automatic-upgrade copy, block indexing, cleanup/versioning controls, connection management, copy helpers, database/configuration paths, debug labels, and many newer status strings. The two empty translations are higher risk than missing keys because they may produce blank UI text. Not being listed in `valid-langs.js` creates a visible-integration risk.

### Test signals
Run JSON parse validation, key coverage diff, placeholder parity, and an explicit empty-value check. If enabling Vietnamese in the language list, first resolve empty entries and smoke-test settings, folder/device editing, notifications, logs, and version restore flows for fallback or blank labels.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-vi.json -->
