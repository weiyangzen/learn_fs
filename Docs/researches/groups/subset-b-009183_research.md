# Research: subset-b-009183 Syncthing GUI language catalogs

This grouped report covers five generated Syncthing GUI translation catalogs under `sources/sync-backup/syncthing/gui/default/assets/lang/`. Each section is source-tree aligned so the reconciliation lane can split it into the mapped per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fr.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fr.json

## Purpose

`lang-fr.json` is the French runtime translation catalog for the Syncthing AngularJS web GUI. It maps English source strings used by `translate` attributes, Angular translate filters, and `$translate.instant(...)` calls to French strings. It is loaded on demand as `assets/lang/lang-fr.json` when the selected locale is `fr`.

The language directory README says these files are generated and should not be edited directly; translation updates are expected to flow from Weblate into this JSON asset. `fr` is listed in both `valid-langs.js` and `prettyprint.js`, so the GUI language selector exposes it as `French`.

## Important APIs, Types, and Data Shape

The file is a JSON object with 558 top-level keys. Of those, 557 values are strings and one value is the nested `theme.name` object:

```json
"theme": {
  "name": {
    "black": "Noir",
    "dark": "Sombre",
    "default": "Par defaut (systeme)",
    "light": "Clair"
  }
}
```

The keys are the English message IDs extracted by `script/translate.go`. Most IDs are literal UI text such as `Add Folder`, `Restart`, and `Out of Sync Items`; some contain interpolation placeholders like `{%device%}`, `{%folder%}`, and `{%version%}`. The generator normalizes these placeholders to Angular-style `{{device}}` values in translation output, while the source key remains the `{%...%}` ID.

Runtime consumers are not functions in this file, but the effective API is the catalog contract expected by Angular Translate:

- `syncthing/app.js` configures `$translateProvider.useStaticFilesLoader({ prefix: 'assets/lang/lang-', suffix: '.json' })`.
- `$translateProvider.fallbackLanguage('en')` makes `lang-en.json` the fallback for missing IDs.
- `LocaleService` calls `$translate.use(language)` and sets `document.documentElement.lang` after a successful load.
- `languageSelectDirective.js` uses `LocaleService.getAvailableLocales()` and `langPrettyprint` to expose `fr` in the dropdown.

## Control Flow and Integration Points

On startup, `LocaleService.autoConfigLocale()` chooses the locale from `?lang=`, browser localStorage, or `/rest/svc/lang`. If `fr` is selected or negotiated, Angular Translate requests `assets/lang/lang-fr.json`. Templates and controllers then resolve message IDs through the loaded catalog, falling back to English for any missing entry.

The authentication layer explicitly allows `/rest/svc/lang` without login so the login page can choose a language before authentication. Static assets under `/assets/` are also allowed without auth, so this catalog can load on both login and authenticated screens.

Generation and maintenance integrate with:

- `script/weblatedl.go`, which downloads Weblate translations, writes `lang-<code>.json`, and refreshes `valid-langs.js` and `prettyprint.js`.
- `script/translate.go`, which scans GUI HTML/JS, builds missing source IDs, and adds theme names from GUI theme directories.
- `assets/lang/README.txt`, which marks these files as generated from hosted Weblate.

## State and Persistence Behavior

The JSON file itself has no mutable state. User language choice is persisted outside the file under the browser localStorage key `SYN_LANG` when the user explicitly changes language. A `?lang=fr` URL parameter overrides stored and browser-negotiated choices and is saved when passed through `LocaleService.useLocale(locale, true)`.

Because this catalog is a static asset, changing it requires regenerating or replacing the asset and having browsers fetch the updated file. Any stale browser or service cache could continue serving old translations until invalidated by normal asset cache behavior.

## Dependencies

Direct runtime dependencies are AngularJS, `pascalprecht.translate`, the static-files loader, `ngSanitize`, `valid-langs.js`, and `prettyprint.js`. The catalog also depends on the English source key set in `lang-en.json`; English keys are the stable IDs used by the GUI.

Build/update dependencies are the Weblate API token used by `script/weblatedl.go`, JSON validity, and the source-string extraction behavior in `script/translate.go`.

## Risks and Edge Cases

The French file currently has complete key coverage against `lang-en.json`: zero missing keys and zero extra top-level keys. Placeholder parity checks found no mismatched placeholder names between source IDs and translated string values. This lowers the risk of broken interpolation in messages such as shared-folder prompts and upgrade notices.

The remaining risks are typical catalog risks: translations can become stale as UI text changes, generated updates can overwrite local edits, and string values that are technically valid JSON can still be semantically wrong or too long for constrained buttons and table columns. Twelve string values equal their English IDs, including short technical or borrowed terms such as `LDAP`, `OK`, and `Version`; these are not necessarily defects but are useful review signals.

## Test Signals

Validation performed for this research:

- `jq -e .` succeeds for the file.
- File size is 57,132 bytes and 567 lines.
- Top-level key count is 558, matching `lang-en.json`.
- Value type distribution is 557 strings and one object.
- Missing keys versus `lang-en.json`: 0.
- Extra keys versus `lang-en.json`: 0.
- Placeholder parity check across string entries found no mismatches.
- Locale registration check confirms `fr` appears in `valid-langs.js` and `prettyprint.js`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fr.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fy.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fy.json

## Purpose

`lang-fy.json` is the Frisian runtime translation catalog for the Syncthing AngularJS web GUI. It supplies translations for the same English message IDs used in templates, filters, and JavaScript translation calls, and it is fetched as `assets/lang/lang-fy.json` when the active locale is `fy`.

The file is generated from Weblate according to the language directory README. `fy` is present in `valid-langs.js` and `prettyprint.js`, so it is offered in the GUI language dropdown as `Frisian`.

## Important APIs, Types, and Data Shape

The file is a JSON object with 441 top-level keys, all with string values. Unlike the current English, French, Irish, Galician, and Hebrew catalogs reviewed in this group, it has no nested `theme` object. That means theme names fall back to English or another fallback translation when Frisian is active.

The effective API is still the Angular Translate static catalog contract:

- English UI strings are lookup IDs.
- Translated strings may include Angular interpolation tokens converted from source placeholders, for example `{{device}}` for a `{%device%}` key.
- The catalog is discovered by locale code through `assets/lang/lang-` plus the active locale plus `.json`.

The supporting code paths are `syncthing/app.js` for `$translateProvider` setup, `LocaleService` for locale selection and persistence, and `languageSelectDirective.js` for the visible language menu.

## Control Flow and Integration Points

When a user chooses Frisian or a browser language preference resolves to `fy`, `LocaleService.useLocale('fy')` calls `$translate.use('fy')`. Angular Translate then loads `assets/lang/lang-fy.json` and resolves UI message IDs against it. Missing IDs use the configured English fallback.

The catalog participates in the same generated translation workflow as other locales:

- `script/weblatedl.go` downloads translations from Weblate, formats locale codes, writes `lang-fy.json`, and updates valid/pretty language lists.
- `script/translate.go` scans HTML and JS for source IDs and adds untranslated source keys plus theme-name keys.
- `assets/lang/README.txt` marks direct edits as out of process because Weblate is the source of truth.

## State and Persistence Behavior

The JSON catalog is immutable runtime data. Language state lives in the browser and Angular translation service: `LocaleService` reads `?lang=`, localStorage key `SYN_LANG`, then `/rest/svc/lang`; explicit user changes are persisted to `SYN_LANG`. After the catalog loads successfully, the HTML document `lang` attribute is set to `fy`.

Because `fy` has incomplete coverage, the persisted language state can produce mixed-language UI: translated strings from this file plus English fallback for missing IDs.

## Dependencies

Runtime dependencies are AngularJS, Angular Translate, the static files loader, `valid-langs.js`, `prettyprint.js`, and the unauthenticated `/rest/svc/lang` endpoint used for negotiation. The file's key set depends on the extraction and merge behavior of `script/translate.go` and on Weblate completion status.

## Risks and Edge Cases

The main risk is coverage. Compared with `lang-en.json`, `lang-fy.json` is missing 117 top-level keys, including newer or operationally important labels such as `Block Indexing`, `Device Group`, `Folder Group`, `Log In`, `Log Out`, `Listener Status`, `Maximum single entry size`, `Extended Attributes`, and the nested `theme` key. There are no extra top-level keys.

Placeholder parity checks found no mismatched placeholder names among existing string entries, so the translated entries that exist should not break interpolation. However, missing keys produce English fallback text, which can be confusing in workflows that mix older translated labels with newer English-only settings. The absence of `theme.name` translations is a visible edge case in theme-related UI.

Six string values equal their English IDs, including `GUI`, `Help`, `LDAP`, and `Type`; this may be acceptable for technical terms but should be treated as a translation review signal.

## Test Signals

Validation performed for this research:

- `jq -e .` succeeds for the file.
- File size is 38,734 bytes and 443 lines.
- Top-level key count is 441.
- Value type distribution is 441 strings and no objects.
- Missing keys versus `lang-en.json`: 117.
- Extra keys versus `lang-en.json`: 0.
- Placeholder parity check across existing string entries found no mismatches.
- Locale registration check confirms `fy` appears in `valid-langs.js` and `prettyprint.js`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-fy.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ga.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ga.json

## Purpose

`lang-ga.json` is the Irish runtime translation catalog for the Syncthing AngularJS web GUI. It is fetched as `assets/lang/lang-ga.json` when the selected or negotiated locale is `ga`, and it translates the English message IDs used throughout GUI templates and controllers.

The file is generated from Weblate and should not be hand edited. `ga` is present in `valid-langs.js` and `prettyprint.js`, so it is listed in the language selector as `Irish`.

## Important APIs, Types, and Data Shape

The file is a JSON object with 558 top-level keys. It has 557 string values and one nested `theme.name` object:

```json
"theme": {
  "name": {
    "black": "Dubh",
    "dark": "Dorcha",
    "default": "Reamhshocru",
    "light": "Solas"
  }
}
```

The catalog schema is consumed by Angular Translate rather than imported by application code directly. English source text is the ID namespace, while nested IDs such as `theme.name.black` are represented as nested JSON objects. Translated strings preserve the placeholder contract used by templates and controllers.

## Control Flow and Integration Points

`syncthing/app.js` configures the static files loader with prefix `assets/lang/lang-` and suffix `.json`; therefore selecting `ga` causes Angular Translate to request this file. `LocaleService` chooses a locale from URL, localStorage, or `/rest/svc/lang`, then calls `$translate.use('ga')` and sets `document.documentElement.lang` to `ga` after loading.

The catalog integrates with GUI markup via `translate` attributes, Angular translate filters, and JavaScript `$translate.instant(...)` calls. It also integrates with the generated language dropdown through `valid-langs.js` and `prettyprint.js`.

Maintenance flows through `script/weblatedl.go` for Weblate downloads and language list updates, and through `script/translate.go` for source-message extraction and theme-key generation.

## State and Persistence Behavior

This file has no internal state. Locale selection state is stored in browser localStorage as `SYN_LANG` when explicitly changed. A `?lang=ga` URL parameter can force the language and save it; otherwise browser language negotiation occurs through `/rest/svc/lang`, which is permitted before authentication.

The file is a static asset, so runtime behavior is deterministic for a given asset version: the same message ID resolves to the same Irish string unless the catalog is regenerated.

## Dependencies

Runtime dependencies are AngularJS, Angular Translate, `ngSanitize`, `LocaleService`, `languageSelectDirective.js`, `valid-langs.js`, `prettyprint.js`, and the static asset server. Source maintenance depends on Weblate and the extraction scripts.

The file depends on `lang-en.json` as the canonical key set. Complete coverage matters because fallback is key-based and untranslated missing IDs are resolved through English.

## Risks and Edge Cases

Irish has full top-level key coverage against `lang-en.json`: zero missing keys and zero extra keys. Placeholder parity checks found no mismatched placeholder names among string entries, which reduces risk in interpolated messages.

The main risks are semantic and layout-oriented rather than structural. Irish translated text may be longer than English in buttons, modals, and table cells; JSON validation cannot detect truncation or layout overflow. Because these files are generated, local manual fixes would be overwritten unless contributed through Weblate. This catalog has zero string values exactly equal to their English IDs, which is a strong translation-completeness signal but does not prove correctness.

## Test Signals

Validation performed for this research:

- `jq -e .` succeeds for the file.
- File size is 52,967 bytes and 567 lines.
- Top-level key count is 558, matching `lang-en.json`.
- Value type distribution is 557 strings and one object.
- Missing keys versus `lang-en.json`: 0.
- Extra keys versus `lang-en.json`: 0.
- Placeholder parity check across string entries found no mismatches.
- Locale registration check confirms `ga` appears in `valid-langs.js` and `prettyprint.js`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ga.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-gl.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-gl.json

## Purpose

`lang-gl.json` is the Galician runtime translation catalog for the Syncthing AngularJS web GUI. It provides translated values for English message IDs and is loaded as `assets/lang/lang-gl.json` when the current locale is `gl`.

The file is generated from Weblate, not intended for direct edits, and `gl` is registered in both `valid-langs.js` and `prettyprint.js` as `Galician`.

## Important APIs, Types, and Data Shape

The file is a JSON object with 550 top-level keys. It has 549 string values and one nested `theme.name` object:

```json
"theme": {
  "name": {
    "black": "Negro",
    "dark": "Escuro",
    "default": "Predeterminado",
    "light": "Claro"
  }
}
```

The catalog's API is the same static Angular Translate dictionary contract used by all Syncthing GUI languages. English strings are IDs; translated strings are values; nested keys support dot-style lookup for generated theme names. Interpolated IDs preserve the placeholder names used by templates and controllers.

## Control Flow and Integration Points

`LocaleService` selects `gl` from a URL override, stored language, or browser language negotiation. It then calls `$translate.use('gl')`, which causes Angular Translate to fetch this catalog using the static-loader prefix/suffix configured in `syncthing/app.js`. GUI templates resolve `translate` directives and filters against the loaded map, with English fallback for missing IDs.

The language selector integrates through `languageSelectDirective.js`: `valid-langs.js` makes `gl` selectable, and `prettyprint.js` provides the displayed name.

Generation integrates through the Weblate download script and source extraction script. The extraction script also ensures theme directories become translation IDs under `theme.name`.

## State and Persistence Behavior

The catalog is static and stateless. User selection persistence is handled by `LocaleService` with localStorage key `SYN_LANG`; successful locale use updates the document `lang` attribute to `gl`. The unauthenticated `/rest/svc/lang` endpoint helps choose a default before login, while `/assets/` is allowed as a static unauthenticated prefix for catalog loading.

## Dependencies

Runtime dependencies include AngularJS, Angular Translate, the static file loader, the GUI asset server, `valid-langs.js`, `prettyprint.js`, and the canonical English catalog for fallback. Maintenance dependencies are Weblate, `WEBLATE_TOKEN` for downloads, and the Go scripts under `script/`.

## Risks and Edge Cases

Compared with `lang-en.json`, the Galician catalog is missing 8 top-level keys and has no extra top-level keys. Missing entries include `Block Indexing`, `Device Group`, `Folder Group`, `Hint: only deny-rules detected while the default is deny. Consider adding "permit any" as last rule.`, the block-indexing help text, optional group help text for devices and folders, and `Starting`. Those IDs will fall back to English when the Galician locale is active.

Placeholder parity checks found no mismatched placeholder names among translated string entries. Six values equal their English IDs, including `Info`, `LDAP`, `OK`, `QUIC LAN`, `QUIC WAN`, and `Simple`; most are technical or short UI terms, but they remain review signals.

The user-visible risk is mixed-language configuration surfaces, especially around newer folder/device grouping and block-indexing settings. Since the file is generated, corrections should be made through Weblate rather than local patches.

## Test Signals

Validation performed for this research:

- `jq -e .` succeeds for the file.
- File size is 49,513 bytes and 559 lines.
- Top-level key count is 550.
- Value type distribution is 549 strings and one object.
- Missing keys versus `lang-en.json`: 8.
- Extra keys versus `lang-en.json`: 0.
- Placeholder parity check across string entries found no mismatches.
- Locale registration check confirms `gl` appears in `valid-langs.js` and `prettyprint.js`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-gl.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-he-IL.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-he-IL.json

## Purpose

`lang-he-IL.json` is the Hebrew (Israel) runtime translation catalog for the Syncthing AngularJS web GUI. It is loaded as `assets/lang/lang-he-IL.json` when the active locale is `he-IL`, translating English message IDs used across the GUI.

The file is generated from Weblate, and `he-IL` is listed in `valid-langs.js` and `prettyprint.js` as `Hebrew (Israel)`, making it available in the GUI language selector.

## Important APIs, Types, and Data Shape

The file is a JSON object with 551 top-level keys. It has 550 string values and one nested `theme.name` object:

```json
"theme": {
  "name": {
    "black": "שחור",
    "dark": "כהה",
    "default": "ברירת מחדל",
    "light": "בהיר"
  }
}
```

The catalog is consumed through Angular Translate's static file loader. English strings are lookup IDs; translated Hebrew strings are values; nested theme IDs are represented as objects. Interpolation placeholders are part of the data contract and must match the source ID variables.

## Control Flow and Integration Points

Locale selection flows through `LocaleService`: URL parameter, persisted `SYN_LANG`, or browser language data from `/rest/svc/lang`. Calling `$translate.use('he-IL')` loads this file using the static loader configured in `syncthing/app.js`; translated strings are then applied by template `translate` attributes, translate filters, and JavaScript `$translate.instant(...)` calls.

The dropdown is provided by `languageSelectDirective.js`, which displays `Hebrew (Israel)` using the `prettyprint.js` global and limits available choices through `valid-langs.js`.

Generation and maintenance are driven by `script/weblatedl.go`, `script/translate.go`, and the Weblate source noted in `assets/lang/README.txt`.

## State and Persistence Behavior

The JSON file is static data. Persistent user language choice is external to the file and stored as `SYN_LANG` in localStorage when explicitly selected. Successful use of this locale sets the HTML `lang` attribute to `he-IL`.

The catalog does not itself set text direction. Any right-to-left behavior depends on browser/layout handling elsewhere; this file provides Hebrew strings but no `dir="rtl"` metadata. That makes RTL layout review especially important for this locale.

## Dependencies

Runtime dependencies are AngularJS, Angular Translate, the static file loader, `LocaleService`, `valid-langs.js`, `prettyprint.js`, and the GUI static asset serving rules. The unauthenticated `/rest/svc/lang` endpoint and `/assets/` prefix allow language negotiation and catalog loading before login.

Maintenance dependencies are Weblate, the Weblate token used by the download script, JSON validity, and the English source catalog used as the key baseline.

## Risks and Edge Cases

Compared with `lang-en.json`, Hebrew is missing 7 top-level keys and has no extra top-level keys. Missing entries include `Block Indexing`, `Device Group`, `Folder Group`, the block-indexing help text, optional group help text for devices and folders, and `Starting`; those strings will fall back to English.

Placeholder parity checks found no mismatched placeholder names among translated string entries. Five string values equal their English IDs: `LDAP`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`; these are technical labels and may be intentional.

The largest locale-specific risk is RTL rendering. The file contains Hebrew strings but does not encode directionality, and the Angular loader only sets `document.documentElement.lang`. Mixed English fallback strings inside Hebrew UI can also create bidi and readability issues in the missing-key areas.

## Test Signals

Validation performed for this research:

- `jq -e .` succeeds for the file.
- File size is 55,245 bytes and 560 lines.
- Top-level key count is 551.
- Value type distribution is 550 strings and one object.
- Missing keys versus `lang-en.json`: 7.
- Extra keys versus `lang-en.json`: 0.
- Placeholder parity check across string entries found no mismatches.
- Locale registration check confirms `he-IL` appears in `valid-langs.js` and `prettyprint.js`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-he-IL.json -->
