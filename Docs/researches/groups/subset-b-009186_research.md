# sources/sync-backup/syncthing/gui/default/assets/lang localization JSON research

Work item: `subset-b-009186`

The files in this group are Syncthing GUI localization dictionaries loaded by the AngularJS frontend. Each top-level string key is normally the English source phrase used by `translate` directives or `$translate.instant(...)`; the value is the locale-specific phrase. Several complete locales also include a nested `theme.name.*` object consumed by `themeName()` for GUI theme display labels.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-nl.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-nl.json

## Purpose

`lang-nl.json` supplies Dutch translations for the Syncthing default web GUI. It is a generated Weblate asset under `gui/default/assets/lang`; the adjacent `README.txt` says the files are auto-generated and should be updated through Weblate rather than by hand.

The file is a JSON object with 551 top-level entries. Compared with `lang-en.json`'s 558 entries, it is missing 7 English source keys: `Block Indexing`, `Device Group`, `Folder Group`, `Maintain an index of all blocks in the folder...`, `Optional group for the device...`, `Optional group for the folder...`, and `Starting`. It has no extra keys versus English and no empty string values.

## Important APIs, Types, and Data Shape

There are no executable functions or classes. The exported API is the static JSON translation table fetched by angular-translate's static file loader. Most entries are `string -> string` phrase mappings, for example UI labels, warning text, modal copy, tooltip text, status strings, and file operation terms.

One top-level value is an object: `theme.name` maps theme IDs such as `black`, `dark`, `default`, and `light` to Dutch display names. This nested object is important because `syncthing/core/syncthingController.js` calls `$translate.instant("theme.name." + theme)` in `themeName()`.

Interpolation placeholders follow the project convention where source keys contain markers like `{%name%}` and translated values use Angular interpolation such as `{{name}}`. That is expected by angular-translate and `$interpolate`; it should not be treated as a mismatch by tests.

## Control Flow and Runtime Use

`syncthing/app.js` configures `$translateProvider.useStaticFilesLoader({ prefix: 'assets/lang/lang-', suffix: '.json' })` and sets fallback language `en`. When Dutch is selected, angular-translate loads `assets/lang/lang-nl.json`, merges it into the translation table for locale `nl`, and uses entries from this file to resolve `translate` directives and `translate` filters in `index.html` and modal templates.

Locale selection is mediated by `LocaleService` in `syncthing/core/localeService.js`. The service receives available locales from `validLangs`, reads the browser's accepted language list from `/rest/svc/lang`, honors a `?lang=` query parameter, and calls `$translate.use(language)`. Because `valid-langs.js` includes `nl`, Dutch appears in the language selector and can be selected by users.

When a Dutch key is absent, angular-translate falls back to English because `fallbackLanguage('en')` is configured. For the 7 missing Dutch entries, the GUI will therefore show English text rather than fail.

## State and Persistence Behavior

This file has no mutable state. Its runtime effect becomes part of angular-translate's in-memory translation table after the static JSON request succeeds.

User language preference is persisted outside this file by `LocaleService` under the `localStorage` key `SYN_LANG` when selection is made through the UI or `?lang=`. The document `<html lang>` attribute is updated to the active language after `$translate.use(...)` succeeds.

## Dependencies and Integration Points

Primary dependencies are `pascalprecht.translate`, `angular-translate-loader-static-files`, Angular `$interpolate`, and the global `validLangs` / `langPrettyprint` assets. The source phrases are referenced across `index.html` and templates in `syncthing/{core,device,folder,settings,transfer,usagereport}`.

The file is integrated by name: locale code `nl` maps directly to `lang-nl.json`. It also participates in theme display via `theme.name.*`.

## Risks

The main functional risk is drift from `lang-en.json`: missing keys silently fall back to English, which can produce mixed-language UI. The currently observed missing keys are around block indexing and device/folder grouping, so those newer settings may be less localized.

Thirteen string entries have values identical to their keys. Many are abbreviations or technical terms (`GUI`, `LDAP`, `QUIC LAN`, `TCP WAN`), but entries such as `Help`, `Info`, `Type`, and `items` should be checked by Dutch reviewers because exact equality may indicate intentionally borrowed words or untranslated leftovers.

Because this is generated content, manual edits are at risk of being overwritten by Weblate synchronization.

## Test Signals

Useful checks are: `jq` parses the file; all top-level values are strings except the expected `theme` object; no value is empty; keys stay a subset of `lang-en.json` unless the translation system intentionally adds locale-only aliases; placeholder variables in translated values remain compatible with the source phrase; and `valid-langs.js` continues to include `nl`.

Runtime smoke coverage should open the GUI with `?lang=nl`, verify that the language selector lists Dutch, confirm `SYN_LANG=nl` is persisted after selection, and inspect settings screens for English fallback around the 7 missing keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-nl.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-nn.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-nn.json

## Purpose

`lang-nn.json` supplies Norwegian Nynorsk translations for the Syncthing default web GUI. Like the surrounding files, it is generated from Weblate and is not intended for direct hand editing.

The file is a JSON object with 257 top-level entries, all strings. It is much more partial than the English baseline of 558 keys: 301 English keys are absent, no extra keys are present, and there are no empty string values. It also lacks the nested `theme` object found in more complete locales.

## Important APIs, Types, and Data Shape

There are no executable APIs, only static translation data. Every entry maps an English GUI phrase to a Nynorsk string. The entries cover common labels and workflows such as device/folder add dialogs, sharing, file versioning, discovery, error copy, and basic status text, but many newer or less common screens fall back to English.

Unlike the other files in this group, `lang-nn.json` does not define `theme.name.*`. Calls to `$translate.instant("theme.name." + theme)` will not find locale-specific Nynorsk theme labels; the controller's `themeName()` fallback then title-cases the raw theme ID.

Interpolation entries use the same project pattern as other locales: source keys use `{%...%}` markers while translated values use Angular `{{...}}` variables.

## Control Flow and Runtime Use

The generic loader in `syncthing/app.js` can request this file as `assets/lang/lang-nn.json` if `$translate.use('nn')` is called. Once loaded, angular-translate uses it for directives and filters whose English source phrase is present.

However, `assets/lang/valid-langs.js` does not include `nn`. That means `LocaleServiceProvider.setAvailableLocales(validLangs)` does not advertise Nynorsk to automatic browser-language matching or to the language selector. A direct `?lang=nn` query can still call `LocaleService.useLocale('nn', true)` because `useLocale` does not itself check `_availableLocales`, but Nynorsk is effectively hidden from normal UI selection and auto-detection in this snapshot.

Missing Nynorsk keys fall back to English through `$translateProvider.fallbackLanguage('en')`. This is particularly visible because more than half of the English catalog is absent.

## State and Persistence Behavior

The file is immutable static data at runtime. If a user forces Nynorsk through `?lang=nn`, `LocaleService` can persist `SYN_LANG=nn` in `localStorage` and set `<html lang="nn">` after angular-translate loads the file successfully.

Since `nn` is not in `validLangs`, a persisted `SYN_LANG=nn` can still be used on later visits, but the language selector builds its menu from `validLangs` and will not include a normal Nynorsk option.

## Dependencies and Integration Points

The runtime dependencies are the same angular-translate static loader and Angular interpolation stack used by all GUI translations. Integration with `LocaleService` is weaker than for the other files because the locale is not present in `valid-langs.js`.

The file integrates with any template or controller translation ID matching one of its 257 keys. It does not integrate with the theme display path because `theme.name.*` is absent.

## Risks

The largest risk is product exposure ambiguity: the file exists and can be loaded by locale code, but the whitelist omits `nn`. This may mean the translation is intentionally incomplete and not offered, or it may be an asset/list drift bug.

The second risk is extensive English fallback. Missing coverage includes authentication, advanced settings, block indexing, crash reporting, discovery/listener details, restore flows, local changes, login/logout strings, extended attributes, ownership, and many warning texts. A Nynorsk session will therefore present a mixed-language GUI.

Only one entry is identical to the key (`LDAP`), which is likely a technical acronym rather than a translation defect. The absence of `theme.name.*` causes theme labels to fall back to title-cased IDs.

Manual edits are likely to be overwritten because translations are generated through Weblate.

## Test Signals

Static checks should verify valid JSON, no empty values, and expected all-string top-level values for this partial file. Catalog checks should explicitly report its 301 missing keys and the absence of `theme.name.*`.

Integration checks should decide whether `nn` should be in `valid-langs.js`. If it should be user-selectable, tests should assert that the language dropdown includes it and that browser `nn` accept-language values can select it. If it is intentionally hidden, tests should still verify that a direct `?lang=nn` load either works cleanly with fallback or is deliberately blocked.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-nn.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-pl.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-pl.json

## Purpose

`lang-pl.json` supplies Polish translations for the Syncthing default web GUI. It is generated from the project's Weblate translation pipeline and represents a complete locale catalog for this snapshot.

The file is a JSON object with 558 top-level entries, matching `lang-en.json`. It has no missing or extra keys relative to English and no empty string values.

## Important APIs, Types, and Data Shape

This is static data rather than executable code. The top-level API is the translation dictionary consumed by angular-translate. It contains 557 string phrase mappings plus the nested `theme.name` object for theme display names.

The string keys are English source phrases used in templates and JavaScript. Values are Polish translations, with Angular interpolation syntax (`{{name}}`, `{{folder}}`, etc.) where dynamic values are needed. The nested `theme.name` object maps theme identifiers to Polish names such as black, dark, default, and light equivalents.

## Control Flow and Runtime Use

When `LocaleService` selects Polish, `$translate.use('pl')` causes angular-translate's static file loader to fetch `assets/lang/lang-pl.json`. Translated values then populate all `translate` directives, filter calls, and `$translate.instant(...)` calls that use English source phrases as IDs.

`valid-langs.js` includes `pl`, so Polish participates in the language dropdown and in automatic matching from `/rest/svc/lang`. Missing-key fallback is still configured globally to English, but this catalog currently matches English key coverage.

`themeName()` uses `theme.name.*` through `$translate.instant`. Because this file defines `theme.name`, theme labels should be localized instead of falling back to title-cased raw IDs.

## State and Persistence Behavior

The JSON file itself has no state. After successful loading, angular-translate keeps the Polish table in memory.

The active language is managed by `LocaleService`: a user selection can be stored as `SYN_LANG=pl` in browser `localStorage`, and the document language is set to `pl`. Those persistence behaviors are external to the JSON but depend on this file loading successfully.

## Dependencies and Integration Points

The file depends on the frontend's translation infrastructure: `pascalprecht.translate`, `angular-translate-loader-static-files`, Angular interpolation, `valid-langs.js`, and `prettyprint.js` for display names. It integrates with most user-facing GUI areas, including device management, folder configuration, advanced settings, networking/discovery status, file version restore flows, usage reporting, and warnings.

The filename must remain aligned with locale code `pl`, because the loader constructs the URL from the locale string.

## Risks

The main maintenance risk is placeholder drift when English source phrases change. Dynamic values must keep compatible Angular interpolation variables in the Polish value. Because fallback uses English, any future missing key will produce mixed-language UI rather than a hard failure.

Nine values are identical to their English keys: `Folder`, `GUI`, `LDAP`, `OK`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, `TCP WAN`, and lowercase `folder`. Most are acronyms, protocol labels, or terms that may intentionally be unchanged, but they are useful review signals.

Because the file is generated, direct local edits can be overwritten by the Weblate update flow.

## Test Signals

Static tests should parse with `jq`, assert 558 keys against `lang-en.json`, assert zero missing and zero extra keys, assert no empty strings, and verify the `theme.name` object is present.

Runtime smoke tests should load `?lang=pl`, check that Polish is visible in the language dropdown, confirm `SYN_LANG=pl` persistence after selection, verify representative interpolated strings render with dynamic values, and inspect the GUI theme selector for Polish theme names.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-pl.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-pt-BR.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-pt-BR.json

## Purpose

`lang-pt-BR.json` supplies Brazilian Portuguese translations for the Syncthing default web GUI. It is generated from Weblate-managed translations and is part of the static frontend assets.

The file is a JSON object with 558 top-level entries, matching `lang-en.json`. It has no missing or extra keys relative to English and no empty string values.

## Important APIs, Types, and Data Shape

The file's API surface is a JSON translation table. It contains 557 top-level string translations and one nested `theme.name` object. The keys are English source phrases from GUI templates/controllers; values are Brazilian Portuguese strings.

Dynamic text uses Angular interpolation in translated values, for example `{{name}}`, `{{device}}`, or `{{folder}}`, while source IDs often contain `{%...%}` placeholders. That transformation is expected by angular-translate and the GUI templates' `translate-value-*` attributes.

The `theme.name` object supplies localized names for theme IDs consumed by `themeName()` in `syncthingController.js`.

## Control Flow and Runtime Use

When the active locale is `pt-BR`, angular-translate loads `assets/lang/lang-pt-BR.json` via the static file loader configured in `syncthing/app.js`. Translations are then used throughout the AngularJS GUI by `translate` directives, filters, tooltip expressions, and `$translate.instant(...)`.

`pt-BR` is present in `valid-langs.js`, so it is available in the language selector and can be selected automatically from matching browser accept-language values returned by `/rest/svc/lang`.

The global fallback language is English. Since this file currently has full English key coverage, fallback should mainly matter if future source strings are added without Brazilian Portuguese translations.

## State and Persistence Behavior

The file is static and immutable at runtime. angular-translate caches the loaded table in memory for the selected locale.

Selection and persistence are handled by `LocaleService`; choosing Brazilian Portuguese can store `SYN_LANG=pt-BR` in browser `localStorage`, and the document's `lang` attribute is updated to `pt-BR` after successful language activation.

## Dependencies and Integration Points

Dependencies include angular-translate, the static files loader, Angular interpolation/sanitization, `valid-langs.js`, and `prettyprint.js` for the user-facing locale name. The file integrates with the full default GUI surface: navigation, settings, device and folder modals, discovery/listener status, file versioning, restore actions, local changes, usage reporting, and warnings.

Its filename is part of the runtime contract: `$translate.use('pt-BR')` maps to `assets/lang/lang-pt-BR.json`.

## Risks

The primary risk is future catalog drift: new English keys without translations will silently fall back to English. Placeholder mistakes are also high impact because they can remove device names, folder IDs, URLs, counts, or other dynamic values from warning and confirmation text.

Eight values are identical to their English keys: `LDAP`, `OK`, `QUIC LAN`, `QUIC WAN`, `Relay LAN`, `Relay WAN`, `TCP LAN`, and `TCP WAN`. These are likely intentionally untranslated acronyms/protocol labels but remain useful review signals.

As generated Weblate output, local manual edits should be avoided.

## Test Signals

Static validation should parse the JSON, compare key sets with `lang-en.json`, assert no missing/extra keys, assert no empty string values, verify the `theme.name` object, and check that interpolation variables remain present in translated strings.

Runtime validation should load the GUI with `?lang=pt-BR`, verify the selector exposes Brazilian Portuguese, confirm `SYN_LANG=pt-BR` persistence, inspect a few interpolated modals and tooltips, and verify localized theme names in the settings dialog.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-pt-BR.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-pt-PT.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-pt-PT.json

## Purpose

`lang-pt-PT.json` supplies European Portuguese translations for the Syncthing default web GUI. It is a generated Weblate translation asset loaded by the AngularJS frontend.

The file is a JSON object with 548 top-level entries. Compared with `lang-en.json`'s 558 entries, it is missing 10 keys: `Block Indexing`, `Debug`, `Device Group`, `Folder Group`, `Info`, `Limit Bandwidth in LAN`, `Maintain an index of all blocks in the folder...`, `Optional group for the device...`, `Optional group for the folder...`, and `Starting`. It has no extra keys and no empty string values.

## Important APIs, Types, and Data Shape

This file contains static localization data rather than functions. It exports 547 string mappings plus a nested `theme.name` object. Top-level string keys are English source phrases used by templates and controllers; values are European Portuguese translations.

Translated values use Angular interpolation markers such as `{{name}}`, `{{count}}`, and `{{receiveEncrypted}}` for runtime values. The source keys often use the Syncthing translation placeholder notation `{%...%}`; angular-translate resolves the translated value through Angular `$interpolate`.

The nested `theme.name` object is consumed by `themeName()` for the GUI theme selector.

## Control Flow and Runtime Use

When the active locale is `pt-PT`, `$translate.use('pt-PT')` loads `assets/lang/lang-pt-PT.json` through the static file loader configured in `syncthing/app.js`. The loaded table backs `translate` directives, filters, tooltip translations, and controller calls.

`valid-langs.js` includes `pt-PT`, so European Portuguese is available in the language dropdown and participates in browser-language matching through `LocaleService`.

The globally configured fallback is English. The 10 missing keys will display in English rather than causing errors, with likely visibility in newer settings around block indexing, grouping, LAN bandwidth limiting, and debug/status labels.

## State and Persistence Behavior

The file has no own state and no persistence. angular-translate stores the loaded locale table in memory.

`LocaleService` handles persistence externally: selecting this locale can store `SYN_LANG=pt-PT` in `localStorage`, and the HTML document language is set to `pt-PT` after activation.

## Dependencies and Integration Points

Dependencies are angular-translate, the static file loader, Angular interpolation/sanitization, `valid-langs.js`, and locale display data from `prettyprint.js`. The file integrates with all GUI templates/controllers that use English source phrases as translation IDs.

The `theme.name.*` entries integrate specifically with the settings view's theme selector through `syncthingController.js`.

## Risks

The main risk is partial catalog drift. Missing keys are few but user-visible, and fallback to English can create mixed-language settings and status screens. The missing `Debug` and `Info` labels are short but visible; missing block-indexing and grouping descriptions may affect comprehension of advanced folder/device settings.

Six values are identical to their keys: `LDAP`, `OK`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`. These are likely intentional technical labels.

Because this file is generated, direct edits are fragile and should be made upstream in Weblate.

## Test Signals

Static checks should parse the JSON, compare the key set with English, report the 10 missing keys, assert no extra keys and no empty values, and verify that `theme.name` is present.

Runtime smoke tests should open `?lang=pt-PT`, ensure the language selector lists European Portuguese, verify `SYN_LANG=pt-PT` persistence, exercise settings areas tied to the missing keys to confirm English fallback is acceptable, and inspect interpolated confirmation dialogs for correct dynamic values.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-pt-PT.json -->
