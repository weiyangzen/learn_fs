# subset-b-009181 research

Grouped research report for Syncthing default GUI language catalogs in `sources/sync-backup/syncthing/gui/default/assets/lang`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-el.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-el.json

Purpose: Greek localization catalog for the Syncthing AngularJS web GUI. The file maps English source strings used by `translate` directives and `translate` filters to Greek UI text for device/folder management, authentication, versioning, discovery, crash reporting, transfer status, warning dialogs, and theme names.

Important APIs/types/functions: this is static JSON consumed as an angular-translate static-file table, not executable code. The API surface is the set of translation keys, the translated scalar values, and the nested `theme.name.{black,dark,default,light}` object. Runtime interpolation depends on angular-translate variables converted from source-key tokens such as `{%name%}`, `{%file%}`, `{%foldertype%}`, `{%receiveEncrypted%}`, `{%version%}`, and `{%device%}` to value tokens such as `{{name}}` and `{{device}}`.

Control flow: `syncthing/app.js` configures `$translateProvider.useStaticFilesLoader({ prefix: 'assets/lang/lang-', suffix: '.json' })`, `$translateProvider.fallbackLanguage('en')`, and `LocaleServiceProvider.setAvailableLocales(validLangs)`. When the selected locale is `el`, angular-translate loads this file, resolves template literals by exact key match, escapes interpolation values through `useSanitizeValueStrategy('escape')`, and falls back to `lang-en.json` for missing keys.

State and persistence behavior: the file has no mutable state, browser storage, or persistence writes. Its state is release-time catalog data served as a static asset and cached by the browser/server. I parsed the complete JSON: it contains 546 top-level entries and 549 scalar leaf translations, with one nested `theme.name` object.

Dependencies and integration points: integrated with AngularJS templates across `index.html` and `syncthing/**` views through the `translate` attribute/filter, plus JavaScript-generated strings that call `$translate`. It depends on valid JSON syntax, exact English source keys, and stable placeholder names shared with the templates. The English fallback catalog is a functional dependency because this file is missing 12 top-level keys present in `lang-en.json`.

Risks: missing keys cause mixed Greek/English UI for affected controls. The missing English keys are for block indexing, device/folder grouping, LAN bandwidth limiting, startup/debug/info labels, and two folder-type gating messages. Placeholder mismatch would be higher risk because it can drop runtime values from confirmation and warning text; a complete placeholder scan found 23 placeholder-bearing entries and zero key/value placeholder mismatches. Longer Greek strings may affect modal and table layout, especially compact status columns and buttons.

Test signals: `jq` parsing should succeed; key-count comparison against `lang-en.json` should report the expected 12 missing keys and no extras; placeholder checks should confirm every `{%...%}` key token has the corresponding `{{...}}` value token. GUI smoke tests should switch to Greek and inspect add/remove device, add/remove folder, receive-encrypted warnings, version restore, upgrade, and theme selection flows for fallback English, interpolation, escaping, and layout overflow.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-el.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-en-AU.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-en-AU.json

Purpose: Australian English localization catalog for the Syncthing AngularJS web GUI. It preserves most upstream English wording and overrides a small set of regional spellings/terms such as "synchronised", "bin", and "fewer full scans".

Important APIs/types/functions: this is a static angular-translate JSON catalog. Its externally consumed API is the key/value map of UI strings plus the nested `theme.name` values. Placeholder-bearing keys use source tokens like `{%count%}`, `{%path%}`, `{%url%}`, `{%version%}`, and `{%receiveEncrypted%}` while values use angular-translate interpolation tokens like `{{count}}`, `{{path}}`, `{{url}}`, `{{version}}`, and `{{receiveEncrypted}}`.

Control flow: the Syncthing GUI loader derives this file from locale code `en-AU` using the static-file prefix/suffix in `syncthing/app.js`. If a key is absent, `$translateProvider.fallbackLanguage('en')` supplies the base English value. Interpolated values are escaped before insertion, so translations may safely display user-controlled device names, paths, folder labels, URLs, and version strings when placeholders are preserved.

State and persistence behavior: the catalog is immutable runtime data. It does not read or write application configuration, but it shapes visible text for persisted settings such as GUI authentication, folder defaults, device limits, file versioning, ignored devices/folders, and usage-reporting choices. I parsed the complete JSON: it contains 522 top-level entries and 525 scalar leaf translations, with one nested `theme.name` object.

Dependencies and integration points: depends on angular-translate, the generated `validLangs` list, and the base English catalog for fallback coverage. It integrates with translated strings in `index.html`, modal partials, settings views, folder/device editors, restore-version views, and tooltip expressions such as `{{'Copy' | translate}}`. Compared with `lang-en.json`, it intentionally changes five values: fewer scans, "synchronised" in two strings, "bin" for trash retention text, and "Bin File Versioning".

Risks: this catalog is significantly less complete than base English, missing 36 top-level keys from `lang-en.json`. Missing entries include login/authentication labels, debug/info/startup labels, connection count and QUIC status strings, block-indexing text, group fields, LAN bandwidth limiting, and several validation messages. Because fallback is English, runtime remains functional but the locale experience is inconsistent. Placeholder risk is low in the current file: 23 placeholder-bearing entries were found and none had mismatched variable names.

Test signals: `jq` should parse the file; a key diff against `lang-en.json` should identify the current 36 missing keys and zero extras; placeholder validation should remain clean. Browser checks should select Australian English and inspect authentication, settings, folder defaults, device defaults, versioning, and transfer-error views, because several missing keys are concentrated in newer settings and login surfaces.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-en-AU.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-en-GB.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-en-GB.json

Purpose: British English localization catalog for the Syncthing AngularJS web GUI. It mirrors the full base English key set while changing selected spelling, terminology, and phrasing, for example "synchronisation", "Internet", "dialogue", "fortnightly", and "Rubbish Bin".

Important APIs/types/functions: this JSON file is a complete angular-translate message table. The API is the exact English source-key namespace used by templates and controllers, including nested `theme.name.black`, `theme.name.dark`, `theme.name.default`, and `theme.name.light`. Dynamic strings depend on angular interpolation placeholders such as `{{foldertype}}`, `{{otherFolderLabel}}`, `{{syncthingInotify}}`, `{{folderlabel}}`, and `{{reintroducer}}`.

Control flow: when locale `en-GB` is active, the static-file loader requests `assets/lang/lang-en-GB.json`. Angular-translate resolves exact keys first from this file, then can fall back to `en`, though this catalog currently has no top-level key gaps relative to `lang-en.json`. Escaped interpolation values are inserted into translated values for confirmation prompts, path warnings, version upgrades, and sharing notifications.

State and persistence behavior: the file is static UI data with no control logic or persistence writes. It affects text displayed around persistent Syncthing state, including folders, devices, ignored items, authentication, upgrade channel choice, versioning policies, filesystem watcher state, and rate limits. I parsed the complete JSON: it contains 558 top-level entries and 561 scalar leaf values, with one nested `theme.name` object.

Dependencies and integration points: depends on the Syncthing GUI's AngularJS translation setup in `syncthing/app.js`, the `validLangs` locale list, and all template/controller call sites that use English strings as translation identifiers. It changes 11 scalar values compared with `lang-en.json`, mostly spelling/word choice: "synchronised", "dialogue", "fortnightly", "Rubbish Bin", lowercase "to" in "Upgrade to", and a rewritten Syncthing description.

Risks: because key coverage is complete, fallback-mixing risk is low. The main risks are semantic drift from base English when source text changes, and preserving placeholders through localized rewrites. A complete placeholder scan found 25 placeholder-bearing entries and zero mismatches, so current dynamic prompts should retain all runtime values. Regional terminology can still affect documentation consistency if surrounding docs or screenshots use base English labels like "Trash Can".

Test signals: `jq` parsing should pass; key diff against `lang-en.json` should show zero missing and zero extra top-level keys; placeholder validation should show zero mismatches. GUI smoke tests should select British English and inspect versioning labels, upgrade banner, settings dialog/dialogue text, about text, receive-encrypted warnings, and share-folder prompts to verify regional text and interpolation display correctly.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-en-GB.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-en.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-en.json

Purpose: canonical English fallback catalog for the Syncthing default GUI. It provides the base translation namespace used by angular-translate and acts as the fallback for every other locale under `assets/lang`.

Important APIs/types/functions: although it is data, this file defines the effective public key contract for translated GUI text. Template literals, `translate` attributes, `translate` filters, and JavaScript translation calls all use these English strings as identifiers. It includes flat scalar entries for GUI labels, help text, warnings, statuses, validation messages, file-versioning descriptions, and connection descriptions, plus nested `theme.name.{black,dark,default,light}` values.

Control flow: `syncthing/app.js` registers the static loader with prefix `assets/lang/lang-` and suffix `.json`, then sets `fallbackLanguage('en')` and default locale `en`. If another locale is incomplete or unavailable, angular-translate resolves missing strings here. Placeholder-bearing keys use legacy source tokens such as `{%device%}` while values convert them to angular interpolation syntax such as `{{device}}`; the configured sanitize strategy escapes interpolated values.

State and persistence behavior: the catalog itself is immutable static data. It has a persistence-adjacent role because many strings describe or confirm changes to Syncthing configuration and persisted sync state: adding/removing folders and devices, editing defaults, enabling authentication, selecting upgrade channels, configuring versioning cleanup, ignoring devices/folders, and restoring/deleting files. I parsed the complete JSON: it contains 558 top-level entries and 561 scalar leaf values, with one nested `theme.name` object.

Dependencies and integration points: this file is tightly integrated with the AngularJS GUI templates in `index.html` and `syncthing/**`, the generated language list, angular-translate's static-files loader, and `ngSanitize`. It is also the reference for translators: other locale files are expected to preserve its key set and placeholder variables. Many keys correspond exactly to visible English DOM text, so changing a key requires changing all call sites or adding compatibility entries.

Risks: because English source text is the translation key, copy edits are compatibility-sensitive. Renaming a key without updating templates causes missing translations in every locale; changing only a value can leave regional catalogs stale. Placeholder drift is another risk for dynamic warnings and confirmation prompts. Current scan found 25 placeholder-bearing entries and no key/value placeholder mismatches. There is also UI risk from long strings used in tooltips, modals, and table headers, even in the fallback language.

Test signals: `jq` parsing should pass; all locale comparisons should use this file as the baseline; placeholder validation should confirm each `{%...%}` source token has a matching `{{...}}` value token. End-to-end GUI checks should run with the default `en` locale and cover startup/login, settings, add-device, add-folder, share-folder, restore versions, receive-encrypted warnings, upgrade, ignored items, and theme switching because these areas exercise most dynamic and nested entries.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-en.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-eo.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-eo.json

Purpose: Esperanto localization catalog for the Syncthing AngularJS web GUI. It translates the full base English GUI namespace into Esperanto for the same device, folder, connection, authentication, versioning, discovery, and warning surfaces covered by `lang-en.json`.

Important APIs/types/functions: this is static JSON consumed by angular-translate. The important contract is exact key coverage, value strings, interpolation placeholder preservation, and the nested `theme.name` object. Dynamic entries include device/folder sharing prompts, remove confirmations, path warnings, upgrade text, receive-encrypted warnings, edited path text, deleted/updated file messages, and documentation-link text.

Control flow: selecting locale `eo` causes the configured static loader to fetch `assets/lang/lang-eo.json`; angular-translate then resolves keys from this catalog before consulting the English fallback. Interpolation values supplied by attributes such as `translate-value-device`, `translate-value-folder`, `translate-value-name`, and `translate-value-version` are inserted into the Esperanto strings with escaping enabled.

State and persistence behavior: no mutable state or persistence logic exists in this file. Its translations are static assets, but they label and confirm operations that mutate Syncthing state, including folder/device sharing, rate limits, watcher settings, authentication setup, ignored item lists, upgrade choices, and file restoration. I parsed the complete JSON: it contains 558 top-level entries and 561 scalar leaf values, with one nested `theme.name` object.

Dependencies and integration points: depends on the AngularJS translation stack, the `validLangs` locale list, exact English source keys, and template/controller interpolation names. It integrates with the same GUI views as the base catalog and currently has complete top-level coverage relative to `lang-en.json`, so normal runtime should not need English fallback for known keys.

Risks: key coverage is complete, but translator quality and placeholder preservation remain the main risks. Some long Esperanto text may overflow dense controls or modals. Because this catalog is a full translation rather than a regional English override, stale technical terminology can confuse configuration workflows around receive-encrypted folders, block indexing, ownership/extended attributes, QUIC/TCP connection labels, and versioning cleanup. A complete placeholder scan found 25 placeholder-bearing entries and zero variable mismatches.

Test signals: `jq` should parse the file; key diff against `lang-en.json` should show zero missing and zero extra top-level keys; placeholder validation should remain clean. GUI smoke tests should switch to Esperanto and inspect add/remove device, add/remove folder, connection status, ownership/extended-attribute settings, receive-encrypted warnings, restore versions, ignored items, and theme selection for interpolation, fallback absence, and layout fit.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-eo.json -->
