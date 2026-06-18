# Research: subset-b-009180

Grouped research report for Syncthing GUI locale JSON assets. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ca@valencia.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ca@valencia.json

Purpose: provides Valencian Catalan translations for Syncthing's default AngularJS web GUI. The file is a static JSON translation table consumed by `angular-translate` through `assets/lang/lang-ca@valencia.json`, with English UI strings as lookup keys and translated strings as values. It lets users select or auto-negotiate the `ca@valencia` locale shown as `Valencian` in `prettyprint.js`.

Important APIs/types/functions: there are no executable functions in this file; the data contract is `map[string]any` as used by `script/weblatedl.go` and `script/translate.go`. Most entries are flat English string keys, while `theme.name.{black,dark,default,light}` is a nested object used for theme display names. Interpolation placeholders in source keys use the extraction form `{%name%}` and translated values use Angular interpolation form `{{name}}`; examples include `{{name}}`, `{{label}}`, `{{count}}`, `{{device}}`, `{{folder}}`, and `{{receiveEncrypted}}`.

Control flow: at GUI startup `syncthing/app.js` configures `$translateProvider.useStaticFilesLoader({prefix: 'assets/lang/lang-', suffix: '.json'})` and fallback language `en`. `LocaleService.autoConfigLocale()` chooses a locale from the `?lang=` query parameter, saved `SYN_LANG` localStorage value, or `/rest/svc/lang` browser locale list. When `ca@valencia` is selected, `$translate.use('ca@valencia')` fetches this file; translation filters and directives then resolve keys from templates and controller calls against this table, falling back to English for missing keys.

State and persistence behavior: the file itself is immutable static UI data. Runtime state is external: the chosen locale can be persisted in browser localStorage under `SYN_LANG`, and successful language use sets `document.documentElement.lang` to `ca@valencia`. Translation content is generated/updated from Weblate by `script/weblatedl.go`; the extraction helper `script/translate.go` can add source keys and theme names while preserving existing translations.

Dependencies and integration points: depends on inclusion in `valid-langs.js`, where `ca@valencia` is present, and on `prettyprint.js`, where it is displayed as `Valencian`. It integrates with AngularJS, `pascalprecht.translate`, `ngSanitize`, and Syncthing templates that use `<span translate>`, `{{ 'Key' | translate }}`, and `$translate.instant(...)`. It also has an upstream dependency on Weblate completion thresholds used by `script/weblatedl.go`.

Risks and edge cases: this locale has 525 flattened entries versus 561 in `lang-en.json`, so 36 English keys currently fall back to English. Missing examples include newer login, bandwidth, grouping, and block-indexing labels such as `Authentication Required`, `Connection Management`, `Device Group`, `Folder Group`, `Block Indexing`, and `Limit Bandwidth in LAN`. Placeholder integrity is good in the inspected file: all 23 placeholder-bearing entries preserve the same placeholder names between key and value. Some values equal their English key, such as `Auto Accept`, which may be acceptable terminology or an untranslated remnant. The `@` language code works because the loader builds a URL path from the raw language key; any code that assumes only BCP-47 hyphen separators would need care.

Test signals: `python3 -m json.tool` parses the file successfully. A structural check found 522 top-level keys, 525 flattened translation leaves, no empty values, nested `theme.name`, and no placeholder mismatches. Functional smoke coverage should include selecting `?lang=ca@valencia`, verifying the UI fetches `assets/lang/lang-ca@valencia.json`, confirming translated common actions render, and confirming missing keys fall back to English without breaking interpolation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ca@valencia.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ckb.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ckb.json

Purpose: nominally represents the Central Kurdish (`ckb`) Syncthing GUI locale, but the current file is an empty JSON object. As data, it provides no translations and therefore cannot localize the GUI on its own.

Important APIs/types/functions: the file still conforms to the translation-file type expected by the loader: a JSON object decodable as `map[string]any`. It has no flat translation entries, no nested `theme.name` namespace, and no interpolation placeholders.

Control flow: if `$translate.use('ckb')` is ever called, the static file loader can fetch and parse this file, but every UI lookup misses in the selected language. `angular-translate` then uses the configured fallback language `en`, so the user-visible GUI should remain English rather than showing raw missing keys. In the normal Syncthing language picker path, `ckb` is not listed in `valid-langs.js` and not named in `prettyprint.js`, so it should not be automatically selected from browser negotiation or shown as an available language by `LocaleService`.

State and persistence behavior: the file has no translation state. If a user manually forces `?lang=ckb`, `LocaleService.useLocale(language, true)` can persist `SYN_LANG=ckb` after `$translate.use('ckb')` resolves. That creates a persistent preference for an effectively English UI until the language is changed or localStorage is cleared.

Dependencies and integration points: uses the same `assets/lang/lang-<locale>.json` loader convention as the other locale files, but it is currently disconnected from the supported-locale metadata because `ckb` is absent from `valid-langs.js` and `prettyprint.js`. The Weblate downloader normally filters languages by translation completion and current validity; this empty file looks like a leftover or staged locale artifact rather than an enabled locale.

Risks and edge cases: the main risk is accidental enablement. Adding `ckb` to `valid-langs.js` before translations exist would present a language option that localizes nothing. Because the file is syntactically valid and fetchable, loader-level tests may pass while user-visible coverage is effectively zero. Manual `?lang=ckb` selection can also persist an unsupported language key in `SYN_LANG`.

Test signals: `python3 -m json.tool` parses the file successfully, but it contains 0 top-level keys and 0 flattened leaves compared with 561 flattened English entries. Test coverage should assert that unsupported empty locales are not advertised in the language picker and that manually forcing the locale falls back cleanly to English without console loader or interpolation errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ckb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-cs.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-cs.json

Purpose: provides Czech translations for Syncthing's default AngularJS web GUI. It is a static translation table loaded as `assets/lang/lang-cs.json` when the selected or negotiated locale is `cs`, displayed as `Czech` by the locale UI.

Important APIs/types/functions: this is JSON data, not executable code. It follows the same `translation map[string]any` structure consumed by Syncthing's translation scripts: flat English strings map to Czech values, and the nested `theme.name` object maps theme identifiers to Czech display names. Interpolation-bearing strings preserve Angular placeholders such as `{{name}}`, `{{label}}`, `{{count}}`, `{{device}}`, and `{{folder}}`.

Control flow: `app.js` registers the static translation loader and English fallback. `LocaleService` can choose `cs` from `?lang=cs`, saved localStorage, or `/rest/svc/lang` browser preferences because `cs` is listed in `valid-langs.js`. Once selected, Angular templates and controller code resolve translation IDs against this file. Missing Czech entries are resolved through the English fallback.

State and persistence behavior: the JSON file is static and read-only at runtime. Browser locale choice may be persisted under `SYN_LANG`; `LocaleService.useLocale()` also sets the root HTML `lang` attribute to `cs` after the translation table loads. Source updates flow from Weblate via `script/weblatedl.go` and from source-key extraction via `script/translate.go`.

Dependencies and integration points: integrated with `valid-langs.js` (`cs` is available) and `prettyprint.js` (`cs` is named `Czech`). It depends on `angular-translate` static-file loading, Syncthing HTML translate directives, JavaScript `$translate.instant(...)` keys, and generated theme-name collection from GUI theme directories.

Risks and edge cases: this locale has 520 flattened entries, 41 fewer than `lang-en.json`. Missing items include some recent or specialized UI strings such as `Block Indexing`, `Folder Group`, `Folder Status`, `Limit Bandwidth in LAN`, several connection-type labels (`QUIC LAN`, `Relay WAN`, `TCP LAN`), and newer share text that interpolates `{%devicename%}`. Placeholder integrity is good in the inspected file: all 21 placeholder-bearing entries preserve matching placeholder names. Four values are identical to their keys, which may indicate untranslated technical terms. Because missing entries fall back to English, mixed-language screens are the likely failure mode rather than hard errors.

Test signals: `python3 -m json.tool` parses the file successfully. A structural check found 517 top-level keys, 520 flattened leaves, nested `theme.name`, no empty values, and no placeholder mismatches. Practical tests should select `?lang=cs`, verify common settings/device/folder views render Czech strings, verify fallback for an intentionally missing key, and exercise interpolation-heavy dialogs such as removing a device or sharing a folder.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-cs.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-da.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-da.json

Purpose: provides Danish translations for Syncthing's default AngularJS web GUI. It is loaded as `assets/lang/lang-da.json` for the `da` locale and lets the GUI present Danish labels, help text, warnings, and dialog copy.

Important APIs/types/functions: the file is a JSON translation dictionary with English source strings as lookup keys. It includes 549 flattened translation leaves and the nested `theme.name` namespace for theme labels. Placeholder-bearing translations preserve Angular interpolation variables, including device/folder names and counts, by translating `{%...%}` source placeholders into matching `{{...}}` placeholders in values.

Control flow: Syncthing configures `$translateProvider.useStaticFilesLoader()` with the `assets/lang/lang-` prefix and `.json` suffix, then uses `LocaleService` to select `da` from query parameter, saved `SYN_LANG`, or browser locale negotiation. The selected language table is used by Angular translation directives and filters across core, device, folder, settings, and modal views. English fallback remains active for untranslated Danish keys.

State and persistence behavior: the file is static; mutable language state lives in browser localStorage and the `$translate` service. If explicitly chosen, `da` can be saved as `SYN_LANG`, and the document `lang` attribute is set to `da` after successful loading. Generation and maintenance are handled by Weblate download and source extraction scripts, not by runtime code.

Dependencies and integration points: `da` is present in `valid-langs.js` and mapped to `Danish` in `prettyprint.js`. It integrates with AngularJS, `pascalprecht.translate`, `ngSanitize`, Syncthing's `/rest/svc/lang` locale discovery endpoint, and the translation extraction path that scans templates, JavaScript, and theme directories.

Risks and edge cases: Danish coverage is high but not complete: 12 English entries are absent, including `Block Indexing`, `Device Group`, `Folder Group`, `Limit Bandwidth in LAN`, and folder-type constraint messages such as `Always turned on when the folder type is "{%foldertype%}".` There are 11 values equal to their source key, likely technical labels or untranslated remnants. The inspected 23 placeholder-bearing entries have no placeholder mismatches, reducing the risk of broken interpolation in dialogs. Missing keys should fall back to English, resulting in isolated mixed-language strings.

Test signals: `python3 -m json.tool` parses the file successfully. Structural checks found 546 top-level keys, 549 flattened leaves, nested `theme.name`, no empty values, and zero placeholder mismatches. UI smoke tests should select `?lang=da`, inspect the settings/device/folder modals, verify theme names render, and test interpolation in remove/share/restore confirmation dialogs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-da.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-de.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-de.json

Purpose: provides German translations for Syncthing's default AngularJS web GUI. It is a full static locale table loaded from `assets/lang/lang-de.json` when `de` is selected or negotiated and displayed as `German` in the language UI.

Important APIs/types/functions: this JSON object implements the same translation dictionary contract as the other locale files. It contains 561 flattened leaves, matching `lang-en.json` coverage, including nested `theme.name` values and specialized strings for authentication, connection management, folder/device groups, block indexing, rate limits, sharing, and dialogs. Placeholder-bearing entries preserve Angular interpolation variables such as `{{foldertype}}`, `{{name}}`, `{{label}}`, `{{count}}`, `{{device}}`, `{{folder}}`, `{{folderlabel}}`, and `{{reintroducer}}`.

Control flow: `app.js` configures the static translation loader and fallback language. `LocaleService.autoConfigLocale()` can select `de` from a query parameter, a saved `SYN_LANG`, or the browser locale list returned by `/rest/svc/lang`; `de` is advertised in `valid-langs.js`. Once loaded, Angular's translate directive/filter and `$translate.instant(...)` resolve GUI strings from this table. Because coverage matches English, fallback should rarely be exercised for current keys.

State and persistence behavior: runtime state is limited to the selected language in `$translate`, optional localStorage persistence under `SYN_LANG`, and the root HTML `lang=de` attribute. The data file is produced from translation tooling; `script/weblatedl.go` downloads Weblate JSON for accepted languages, and `script/translate.go` can update source-key coverage from GUI templates, JavaScript, and theme directories.

Dependencies and integration points: integrated with `valid-langs.js` (`de` available) and `prettyprint.js` (`German`). It depends on AngularJS, `pascalprecht.translate`, `ngSanitize`, Syncthing's locale negotiation endpoint, and the extraction/generation scripts. It also participates in theme display via the nested `theme.name` keys.

Risks and edge cases: the main data risks are translation drift and interpolation breakage, but the inspected file has complete key parity with English and zero placeholder mismatches across 25 placeholder-bearing entries. Twelve values equal their English key; many are short technical words or labels where German UI may intentionally keep the term, but they are worth periodic review. German strings can be longer than English, so layout regressions are more plausible than lookup failures in compact buttons, tables, and modal headings.

Test signals: `python3 -m json.tool` parses the file successfully. Structural checks found 558 top-level keys, 561 flattened leaves, nested `theme.name`, no empty values, exact key parity with `lang-en.json`, and no placeholder mismatches. Useful UI tests include selecting `?lang=de`, checking long settings labels for wrapping, exercising interpolation-heavy dialogs, and confirming no fallback/missing-translation warnings for current English keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-de.json -->
