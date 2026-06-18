# subset-b-009187 research

Grouped research report for Syncthing GUI localization payloads in `sources/sync-backup/syncthing/gui/default/assets/lang`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ro-RO.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ro-RO.json

Purpose: Romanian (`ro-RO`) localization table for the Syncthing default AngularJS GUI. It maps English source strings used as translation IDs to Romanian UI text for device/folder management, discovery/listener status, file versioning, usage reporting, ignore patterns, upgrade prompts, authentication, and operational warnings.

Important APIs/types/functions: the file is a JSON translation table consumed by `angular-translate` through `$translateProvider.useStaticFilesLoader({ prefix: 'assets/lang/lang-', suffix: '.json' })` in `syncthing/app.js`. Locale availability is controlled separately by `assets/lang/valid-langs.js`, which includes `ro-RO`. At runtime templates, controllers, and filters call `$translate`/`translate` with the English key; missing values fall back to English because `app.js` sets `$translateProvider.fallbackLanguage('en')`.

Control flow: when the browser locale or user-selected locale resolves to `ro-RO`, the static files loader requests `assets/lang/lang-ro-RO.json`, parses this object, and registers its keys as the active translation table. For every translated UI string, angular-translate first looks in this Romanian table, then in the English fallback table, and finally exposes the missing translation ID when neither table has a value. Controller logic also uses nested theme translation IDs such as `theme.name.dark`; unlike most other locale files this Romanian payload has no `theme` object, so `$scope.themeName()` falls back to title-casing raw theme names.

State/persistence behavior: the file is static frontend state embedded in the web UI assets. It does not persist application data, but the selected language can be retained by the GUI locale/storage layer around `LocaleServiceProvider`. The values include Angular interpolation placeholders such as `{{device}}`, `{{folder}}`, and `{{receiveEncrypted}}`; placeholder compatibility is part of runtime state because those values are substituted from controller scope when dialogs are rendered.

Dependencies/integration points: depends on valid JSON syntax, `valid-langs.js` containing `ro-RO`, `index.html` loading angular-translate and `assets/lang/valid-langs.js`, `syncthing/app.js` configuring the static loader/fallback locale, and GUI templates/controllers using English strings as stable message IDs. It also integrates indirectly with `syncthing/core/syncthingController.js` for theme names via `theme.name.*`.

Coverage and observed signals: `jq` parses the file successfully. It contains 466 top-level entries, all string-valued, compared with 558 entries in `lang-en.json`; 92 English keys are absent and will display from the English fallback. There are no keys that are extra relative to English. 201 entries have values identical to their keys, indicating a large untranslated surface even where a key exists. Missing examples include newer/advanced UI areas such as block indexing, extended attributes, ownership sync, login/logout/path visibility strings, connection-type labels, device/folder groups, LAN bandwidth limiting, listener status, user home, `theme`, and several connection/protocol labels.

Risks: Romanian has the weakest coverage in this group. The absent `theme` object means theme labels are not localized and rely on controller fallback title casing. Many identity translations keep English user-facing text, so coverage metrics can overstate real localization quality. Changes to English message IDs can silently drop Romanian coverage because English strings are the lookup keys. Long Romanian strings may affect modal/table layout, though this file has no embedded HTML values and interpolation placeholders match the English table for string entries present in both files.

Test signals: parse with `jq -e type lang-ro-RO.json`, compare key coverage against `lang-en.json`, verify `ro-RO` remains present in `valid-langs.js`, and run/inspect the GUI with Romanian selected for settings, add-device/add-folder, ignore pattern, versioning, authentication, and theme selection surfaces. Automated checks should compare interpolation token sets against English and flag identity translations or missing nested `theme.name.*` entries.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ro-RO.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ru.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ru.json

Purpose: Russian (`ru`) localization table for the Syncthing default AngularJS GUI. It translates the GUI's English message IDs into Russian for core synchronization status, device/folder workflows, versioning modes, discovery/listener diagnostics, usage and crash reporting, authentication, path visibility, connection type details, and settings labels.

Important APIs/types/functions: the file is loaded by angular-translate's static files loader configured in `syncthing/app.js` with `assets/lang/lang-` and `.json`. `valid-langs.js` lists `ru`, making it selectable/negotiable by the locale service. The table includes one nested `theme` object with `name.black`, `name.dark`, `name.default`, and `name.light`, which is consumed through `$translate.instant("theme.name." + theme)` in `syncthing/core/syncthingController.js`.

Control flow: after locale negotiation chooses `ru`, the GUI fetches and registers this JSON table. Angular-translate resolves each English lookup key against the Russian table and falls back to `lang-en.json` for missing keys. Interpolated dialog/status strings carry Angular `{{...}}` placeholders in values, so controller-provided parameters are substituted after translation.

State/persistence behavior: this is immutable frontend asset state, not durable application configuration. The only user-visible persistence dependency is the selected GUI language/theme state outside this file. The nested theme names are data consumed by controller formatting, while all other entries are direct text translations. The table does not include executable code, but malformed JSON or placeholder drift would break visible UI rendering.

Dependencies/integration points: depends on `index.html` loading angular-translate and `valid-langs.js`, `valid-langs.js` advertising `ru`, the static loader path matching the filename, and the English-key contract used throughout the Angular templates/controllers. Russian entries cover both old and newer GUI domains, including extended attributes, ownership sync, connection status, login/logout, path visibility, and protocol labels.

Coverage and observed signals: `jq` parses the file successfully. It contains 551 top-level entries: 550 string translations plus the nested `theme` object. Compared with 558 English entries, it is missing 7 English keys and has no extra keys. Missing keys are `Block Indexing`, `Device Group`, `Folder Group`, `Maintain an index of all blocks in the folder...`, `Optional group for the device...`, `Optional group for the folder...`, and `Starting`. Only 5 string entries are identical to their English keys: `LDAP`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`, which are plausibly product/protocol labels rather than plain untranslated prose. Placeholder token sets match English for string entries present in both files.

Risks: Russian coverage is high, so main risk is drift from newer English keys for block indexing and grouping controls. Because lookup IDs are long English prose strings, edits to source text can bypass an otherwise good Russian translation until the locale file is updated. Long Russian phrases can be wider than English in dense tables and settings dialogs. Protocol labels intentionally remaining in English should be distinguished from accidental identity translations in tooling.

Test signals: parse with `jq`, compare keys against `lang-en.json`, ensure `ru` remains in `valid-langs.js`, and smoke test Russian UI flows for add/edit folder, add/edit device, advanced settings, ignore patterns, versioning, login/logout, connection status, and theme selection. Regression checks should include placeholder-set comparison and a small allowlist for identity protocol/product labels.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ru.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-si.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-si.json

Purpose: Sinhala (`si`) localization table for the Syncthing default AngularJS GUI. It provides Sinhala text for common GUI actions, folder/device sharing, synchronization status, versioning, discovery, warning dialogs, authentication-related prompts, and newer settings areas where translations are available.

Important APIs/types/functions: the file is a JSON translation table loaded by angular-translate via the static files loader in `syncthing/app.js`. `valid-langs.js` includes `si`, which allows locale negotiation/selection to request `assets/lang/lang-si.json`. The table includes a nested `theme` object with localized `theme.name.black`, `theme.name.dark`, `theme.name.default`, and `theme.name.light` values used by `syncthingController.js` when displaying theme choices.

Control flow: when the active GUI locale is Sinhala, the frontend downloads this JSON file, registers it as the current translation table, and resolves English message IDs against it. Keys absent from this table are resolved through the configured English fallback. String values that include Angular interpolation placeholders, such as device, folder, or `receiveEncrypted` names, are interpolated by angular-translate after lookup.

State/persistence behavior: the file is static web asset state. It carries no application persistence, but it controls user-facing state labels, warnings, and form help text. The nested `theme` object is skipped by generic scalar text processing in parts of the controller but is directly addressable through dotted translate IDs. Sinhala text is non-ASCII throughout, so UTF-8 preservation by packaging and serving layers is required.

Dependencies/integration points: depends on angular-translate, the static loader path convention, `valid-langs.js`, English source strings remaining stable as IDs, and GUI code using `$translate`/`translate` consistently. It intersects with device/folder modals, usage-report prompts, version restoration, ignore pattern help, listener/discovery status, and theme-name rendering.

Coverage and observed signals: `jq` parses the file successfully. It contains 507 top-level entries: 506 string translations plus the nested `theme` object. Compared with English's 558 entries, 51 English keys are missing and there are no extra keys. Missing areas include folder-type constraints, connection management/rate-limit text, extended attributes, ownership sync, device/folder grouping, login/logout/path visibility strings, listener status, LAN bandwidth limiting, relay labels, and some newer status/help text. Six string entries are identical to English: `GUI`, `LDAP`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`. Placeholder token sets match English for shared string entries.

Risks: medium coverage gap. Missing keys cause English fallback inside an otherwise Sinhala interface, especially in newer advanced settings. Sinhala glyph rendering depends on browser/font support and can affect line height and wrapping in dense controls. English-key lookup makes source-copy churn a localization risk. Identity protocol labels may be acceptable, but broad untranslated areas should not be hidden by the fallback behavior during testing.

Test signals: validate JSON with `jq`, compare key coverage and interpolation placeholders against `lang-en.json`, verify `si` remains listed in `valid-langs.js`, and smoke test Sinhala across folder/device modals, advanced settings, ignore patterns, versioning, authentication, connection status, and theme selection. Visual testing should include narrow layouts to catch Sinhala wrapping or clipping.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-si.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sk.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-sk.json

Purpose: Slovak (`sk`) localization table for the Syncthing default AngularJS GUI. It translates the English message IDs used by the GUI into Slovak for common actions, device/folder configuration, synchronization and discovery status, file versioning, authentication, connection details, settings, and operational warnings.

Important APIs/types/functions: the JSON table is consumed by angular-translate through the static files loader configured in `syncthing/app.js`. `valid-langs.js` includes `sk`, enabling this file to be selected by the locale service. The table includes a nested `theme` object for `theme.name.black`, `theme.name.dark`, `theme.name.default`, and `theme.name.light`, which `syncthing/core/syncthingController.js` resolves with `$translate.instant("theme.name." + theme)`.

Control flow: selecting or negotiating Slovak causes the browser to request `assets/lang/lang-sk.json`. Angular-translate registers the table, resolves each English source string against it, and falls back to English for keys that are not present. Runtime values in dialogs and warnings are substituted through Angular interpolation placeholders embedded in translated values.

State/persistence behavior: this file is static UI state and does not write Syncthing configuration or index data. It influences persistent-looking UI labels, help text, warnings, and theme names, while language choice itself is managed outside the file. UTF-8 Slovak diacritics must be preserved by asset serving and packaging. No values contain HTML markup, reducing sanitization surface.

Dependencies/integration points: depends on `index.html` loading angular-translate, the loader path convention in `app.js`, `valid-langs.js` advertising `sk`, and the English message-ID contract across templates/controllers. It integrates with the same GUI surfaces as the other locale files: folder/device edit flows, ignore/versioning controls, discovery/listener status, usage reporting, crash reporting, authentication, connection status, and theme selection.

Coverage and observed signals: `jq` parses the file successfully. It contains 542 top-level entries: 541 string translations plus the nested `theme` object. Compared with 558 English entries, 16 English keys are missing and there are no extra keys. Missing keys are concentrated in newer advanced controls and a few status labels: folder-type force/disable messages, block indexing and its help text, device/folder groups, device/folder status, `Debug`, `Info`, LAN bandwidth limiting, group help text, `Starting`, `Stay logged in`, and `unknown device`. Seven string entries are identical to English: `LDAP`, `Limit`, `OK`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`. Placeholder token sets match English for shared string entries.

Risks: Slovak coverage is good but not complete; missing advanced controls fall back to English and may be easy to miss in ordinary smoke tests. Identity entries include short UI words (`Limit`, `OK`) that may be acceptable but should be reviewed by localization maintainers. Long translated warnings can wrap differently in dialogs. As with the other locale files, source English copy changes are high impact because the English text is also the lookup key.

Test signals: parse with `jq`, compare keys and interpolation placeholders against `lang-en.json`, verify `sk` remains in `valid-langs.js`, and smoke test Slovak for settings, advanced folder/device options, listener/discovery details, versioning, authentication, connection type display, and theme selection. Tooling should report missing keys and identity strings separately so protocol/product labels do not mask untranslated UI prose.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-sk.json -->
