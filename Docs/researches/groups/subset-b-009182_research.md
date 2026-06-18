# subset-b-009182 research

Grouped research report for Syncthing GUI language assets in `sources/sync-backup/syncthing/gui/default/assets/lang`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-es.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-es.json

Purpose: Spanish translation table for the Syncthing default web GUI. The file maps English message IDs to Spanish UI text and is loaded at runtime as `assets/lang/lang-es.json`.

Important APIs/types/functions: the file itself is a JSON object, not executable code. It is consumed by AngularJS `pascalprecht.translate` through `$translateProvider.useStaticFilesLoader({prefix: 'assets/lang/lang-', suffix: '.json'})` in `gui/default/syncthing/app.js`. Locale selection flows through `LocaleService.useLocale`, `$translate.use(language)`, and `document.documentElement.lang`. The nested `theme.name` object supports `$translate.instant("theme.name." + theme)` in `syncthingController.js`.

Control flow: `valid-langs.js` advertises `es`, browser or saved locale selection chooses it, angular-translate fetches this JSON, then templates, filters, directives, and controller calls resolve English source strings to Spanish strings. Missing keys would fall back to English because app configuration sets `$translateProvider.fallbackLanguage('en')`.

State and persistence behavior: the translation table is static, generated data. It does not persist application state. The selected language can be stored under `SYN_LANG` in localStorage when selected through a save path, and the loaded table is cached by angular-translate during the page lifetime.

Dependencies and integration points: generated from the upstream translation workflow described by `assets/lang/README.txt`; integrated with `valid-langs.js`, `prettyprint.js`, the Angular translation loader, and all UI views using English literals as translation IDs. The file has 558 top-level keys, matching `lang-en.json` with no missing or extra keys. Its only non-string top-level value is `theme`, an object with `black`, `dark`, `default`, and `light` names.

Risks: Spanish is exposed in `valid-langs.js`, so any invalid JSON blocks a selectable UI language. Interpolated values must preserve Angular variable names from keys such as `{%device%}` as `{{device}}`; checked entries preserve their slots. A small number of values intentionally remain the same as English for protocol labels or short words, but that can also hide untranslated strings.

Test signals: `jq` parses the file as an object; key count equals the English baseline; no missing or extra keys; no empty string values; placeholder scan found no key/value slot mismatches; `valid-langs.js` includes `es`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-es.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-et.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-et.json

Purpose: Estonian translation table for the Syncthing default web GUI. It maps English message IDs to Estonian UI text, but is currently a partial generated asset.

Important APIs/types/functions: the file is a JSON object consumed by angular-translate's static-file loader from `gui/default/syncthing/app.js`. Runtime consumers include `$translate.use(language)`, translation directives and filters in the GUI, and controller lookups such as `$translate.instant("theme.name." + theme)`. The nested `theme.name` object provides localized theme names.

Control flow: if a caller explicitly requests `et`, angular-translate can fetch `assets/lang/lang-et.json`; however `et` is not present in `assets/lang/valid-langs.js`, so normal browser negotiation and the language picker should not advertise it. If loaded anyway, missing translation IDs fall back to English through the configured fallback language.

State and persistence behavior: static generated data only. The asset does not store Syncthing configuration, device state, or folder state. Locale preference persistence is handled outside the file by `LocaleService` via the `SYN_LANG` localStorage key.

Dependencies and integration points: depends on the translation generation pipeline that also writes `valid-langs.js` and `prettyprint.js`. It has 488 top-level keys, all of which are known English IDs, but it is missing 70 English baseline keys. The only non-string top-level value is `theme`, with `black`, `dark`, `default`, and `light` names.

Risks: because the file is not advertised in `valid-langs.js`, it may be a stale or intentionally unlisted translation. Direct `?lang=et` use or a persisted `SYN_LANG=et` value could still load it, producing a mixed Estonian/English UI because of the 70 missing keys. Slot preservation is intact for present interpolated strings, so the main runtime risk is incompleteness rather than malformed interpolation.

Test signals: `jq` parses the file as an object; no extra keys relative to English; 70 missing keys relative to `lang-en.json`; no empty string values; placeholder scan found no key/value slot mismatches; `valid-langs.js` does not include `et`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-et.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-eu.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-eu.json

Purpose: Basque translation table for the Syncthing default web GUI. The file maps English message IDs to Basque UI strings and is available as `assets/lang/lang-eu.json`.

Important APIs/types/functions: this is a generated JSON dictionary consumed by angular-translate. `app.js` configures the static file loader and fallback language; `LocaleService` selects the active language; templates and controllers resolve English source strings through `$translate`. Unlike some neighboring locale files, this file does not include a nested `theme.name` object.

Control flow: `valid-langs.js` includes `eu`, so browser negotiation, explicit `?lang=eu`, or a saved locale can select it. The loader fetches the file and angular-translate resolves keys found here; missing keys fall back to English.

State and persistence behavior: static UI text only. It has no side effects and no persistence of Syncthing runtime state. Language choice persistence is external through `SYN_LANG` in localStorage.

Dependencies and integration points: generated by the translation workflow described in `README.txt`, and coupled to English UI strings used as message IDs. It has 444 top-level keys, no extra keys, and is missing 114 keys relative to `lang-en.json`. It has no non-string top-level values, so theme-name translations are absent and controller theme-name lookups will fall back to title-cased theme IDs when translations are missing.

Risks: the file is selectable but partial, so users will see a mixed Basque/English UI in newer or less translated areas. Two present strings have interpolation variable case mismatches: keys using `{%receiveEncrypted%}` translate the slot as `{{ReceiveEncrypted}}`, which Angular treats as a different expression from `{{receiveEncrypted}}`. Those messages can render a blank or unresolved value depending on scope data.

Test signals: `jq` parses the file as an object; `valid-langs.js` includes `eu`; no extra keys or empty values; 114 missing English baseline keys; placeholder scan found two slot mismatches, both for `receiveEncrypted`; no nested theme translations are present.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-eu.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fa.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fa.json

Purpose: Persian/Farsi translation asset placeholder for the Syncthing default web GUI. The file is valid JSON but contains an empty object, so it contributes no translated UI strings.

Important APIs/types/functions: this file is still compatible with angular-translate's static-file loader because it is a JSON object. If requested as `assets/lang/lang-fa.json`, `$translate.use('fa')` can load it, but all actual translation lookups will miss and fall back to English. There are no nested structures such as `theme.name`.

Control flow: normal UI language discovery should not select this file because `fa` is absent from `assets/lang/valid-langs.js` and `prettyprint.js`. Explicit URL language selection or a stale saved locale can still ask the loader for it. Once loaded, every English translation ID is missing and the configured English fallback supplies display text.

State and persistence behavior: no data state, no local persistence, and no runtime mutation. External locale persistence remains `LocaleService` responsibility through `SYN_LANG`.

Dependencies and integration points: present in the same generated language directory as complete and partial translations, so build packaging may include it even though the GUI does not advertise it. Its empty content suggests either a translation below publication threshold, a stale generated artifact, or a placeholder retained by the sync-backup source snapshot.

Risks: if directly selected, it creates an English UI while `document.documentElement.lang` may be set to `fa`, which can mislead assistive technology, browser spell/typography behavior, and user expectations. It provides no right-to-left translated strings and no theme names. Since no interpolation strings exist, interpolation corruption is not a direct risk.

Test signals: `jq` parses the file as an object; key count is 0; it is missing all 558 English baseline keys; no extra keys or empty string values; `valid-langs.js` does not include `fa`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fa.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fi.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fi.json

Purpose: Finnish translation table for the Syncthing default web GUI. It maps English message IDs to Finnish UI text, but the current asset is partial and not advertised in the active locale list.

Important APIs/types/functions: generated JSON object consumed by the angular-translate static-file loader configured in `app.js`. Locale control flows through `LocaleService` and `$translate`. The file includes a nested `theme.name` object used by controller-side theme display lookups.

Control flow: `fi` is not listed in `valid-langs.js`, so normal language discovery and picker display should not choose it. Explicit `?lang=fi` or a saved `SYN_LANG=fi` can still cause `$translate.use('fi')` to load it. Present keys render Finnish strings; missing keys fall back to English.

State and persistence behavior: static translation data with no direct writes. The only persistence related to it is the user's selected locale in localStorage, handled by `LocaleService`.

Dependencies and integration points: tied to the English key set and translation generator. It has 418 top-level keys, no extra keys, and is missing 140 English baseline keys. The only non-string top-level value is `theme`, with all four expected theme names.

Risks: direct use produces a mixed Finnish/English UI due to missing keys. The file is not in `valid-langs.js`, so it may be intentionally below completion threshold or stale; updating only this file without regenerating `valid-langs.js` would not make it selectable. Placeholder checks on present strings pass, so the largest functional risk is coverage, not runtime expression failure.

Test signals: `jq` parses the file as an object; no extra keys; 140 missing keys versus `lang-en.json`; no empty string values; placeholder scan found no key/value slot mismatches; `valid-langs.js` does not include `fi`; `theme.name` has `black`, `dark`, `default`, and `light`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fi.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fil.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fil.json

Purpose: Filipino translation table for the Syncthing default web GUI. It maps English message IDs to Filipino UI text and is advertised as a selectable GUI language.

Important APIs/types/functions: generated JSON object loaded by angular-translate's static file loader. Runtime consumers are `$translate.use`, translation directives/filters in HTML, and direct `$translate.instant` calls. The nested `theme.name` object supports localized theme display names.

Control flow: `valid-langs.js` includes `fil`, so browser negotiation, the language picker, a saved locale, or `?lang=fil` can select it. The loader fetches `assets/lang/lang-fil.json`; present IDs render Filipino text and the small missing set falls back to English.

State and persistence behavior: no mutable state in the file. Locale preference can be persisted in localStorage under `SYN_LANG`, and angular-translate can cache the loaded table during a session.

Dependencies and integration points: generated from Weblate/translation tooling and paired with `prettyprint.js` for display name `Filipino`. It has 551 top-level keys, no extra keys, and is missing 7 English baseline keys. The only non-string top-level value is `theme`, with the four expected theme names.

Risks: because it is selectable, the 7 missing keys create visible English fallback for specific newer UI concepts such as block indexing and optional device/folder groups. Some values intentionally remain identical to English, especially technical labels; that is valid for names like API terms but can mask untranslated text. Present interpolation slots match their keys.

Test signals: `jq` parses the file as an object; `valid-langs.js` includes `fil`; no extra keys; 7 missing keys versus English; no empty string values; placeholder scan found no key/value slot mismatches; theme names are present.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fil.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fr-CA.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fr-CA.json

Purpose: Canadian French translation table for the Syncthing default web GUI. It maps English message IDs to French Canadian UI text, but the snapshot is partial and not advertised in the active locale list.

Important APIs/types/functions: generated JSON object consumable by angular-translate. The surrounding APIs are the static-file loader in `app.js`, `LocaleService.useLocale`, `$translate.use`, template translation directives, filters, and direct controller translations. This file has no nested `theme.name` object.

Control flow: `fr-CA` is absent from `valid-langs.js`, so normal language discovery will not expose it. Explicit selection can still load `assets/lang/lang-fr-CA.json`. Present keys translate, while missing keys fall back to English. Since no `theme.name` object exists, theme-name lookups fall back to controller title-casing.

State and persistence behavior: static translation data only. User locale persistence, if any, is external in the `SYN_LANG` localStorage value.

Dependencies and integration points: shares the generated language directory with `lang-fr.json`, which is the advertised French locale. It has 240 top-level keys, no extra keys, and is missing 318 English baseline keys. The file covers many older/common GUI labels but omits a large portion of newer interface text.

Risks: direct use results in a heavily mixed French Canadian/English UI and `document.documentElement.lang=fr-CA` despite incomplete translation coverage. Because the locale is not advertised, the file may be stale or below inclusion threshold. Present interpolation slots match, so partial coverage and absent theme names are the primary risks.

Test signals: `jq` parses the file as an object; no extra keys; 318 missing keys versus `lang-en.json`; no empty string values; placeholder scan found no key/value slot mismatches; `valid-langs.js` does not include `fr-CA`; no `theme.name` object.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fr-CA.json -->
