# subset-b-009189 research

Grouped source-tree-aligned research for Syncthing GUI language assets and AngularJS core modules.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-CN.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-CN.json

## Purpose
This file is the Simplified Chinese (`zh-CN`) angular-translate catalog for the Syncthing default web GUI. It maps English source strings used by templates, controllers, notifications, modal text, form labels, validation messages, and status descriptions to Simplified Chinese translations. It is loaded dynamically by the app-level `$translateProvider` static files loader from `assets/lang/lang-zh-CN.json` when `LocaleService` or URL/local-storage/browser negotiation selects `zh-CN`.

## Important APIs, types, and data
The artifact is a JSON object with 558 top-level translation keys. Keys are mostly English UI strings, including interpolation placeholders such as `{{device}}`, `{{folder}}`, and `{{reintroducer}}`, plus some legacy source strings containing `{%device%}` while the translated value uses Angular interpolation. One nested object appears under `theme.name`, with localized theme labels for `black`, `dark`, `default`, and `light`. The catalog includes operational domains such as devices, folders, ignores, versioning, upgrade/restart flows, discovery/listener status, usage reporting, notification acknowledgement, and advanced settings.

## Control flow and integration
There is no executable control flow in the file; runtime behavior comes from angular-translate. `app.js` configures the loader prefix/suffix, `LocaleService` selects the language, and templates/controllers ask `$translate` to resolve source keys. When a key is missing from this catalog, the app falls back to English because `$translateProvider.fallbackLanguage('en')` is configured. `languageSelectDirective.js` exposes `zh-CN` when the global `validLangs` list contains it and displays its English display name from `prettyprint.js`.

## State and persistence behavior
The catalog does not persist state. Language choice can be persisted by `LocaleService` in `localStorage.SYN_LANG`; the JSON file is a static asset fetched by the browser and may be cached by the web server or browser cache. Translation completeness affects displayed UI state but does not modify Syncthing configuration.

## Dependencies and integration points
Primary dependencies are angular-translate's static files loader, `$translate.use('zh-CN')`, `valid-langs.js`, `prettyprint.js`, and all templates/controllers whose literal English keys must exactly match this file. The file also depends on placeholder compatibility with Angular interpolation: translated strings must preserve the variable names expected by the call site.

## Risks
Missing keys silently degrade to English, producing mixed-language UI. Placeholder mismatches can break dynamic messages or display raw variables. HTML-bearing translations are especially sensitive because translation sanitization is configured to escape values; any intended markup must match existing template behavior. This file has one value containing angle brackets, so sanitation and rendering should be checked when editing. Because the source keys are English prose, upstream wording changes can orphan existing translations even when the Chinese text is still conceptually valid.

## Test signals
Useful checks are JSON parsing, diffing key coverage against `lang-en.json`, validating interpolation placeholders per key, selecting `?lang=zh-CN` in the GUI, and smoke-testing dialogs for device/folder share invitations, upgrade warnings, notification acknowledgements, and advanced settings. Automated tests can assert the file is listed in `valid-langs.js`, named in `prettyprint.js`, and contains no invalid JSON or duplicate keys after generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-CN.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-HK.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-HK.json

## Purpose
This file is the Hong Kong Traditional Chinese (`zh-HK`) angular-translate catalog for Syncthing's default GUI. It provides localized UI text for the same source-string based translation system as other language catalogs and is selected when the locale resolver or explicit language selector chooses `zh-HK`.

## Important APIs, types, and data
The artifact is a JSON object with 501 top-level keys. It translates core GUI labels, status strings, folder/device actions, validation messages, usage-report wording, modal titles, and share-invitation text. Like the other catalogs, keys are English source strings and values are localized strings. It contains interpolation values such as `{{device}}`, `{{folder}}`, and `{{folderlabel}}`; the source keys for those entries still use `{%...%}` marker text. Compared with `zh-CN` and `zh-TW`, this catalog has fewer keys, so it likely relies more often on English fallback for newer UI strings.

## Control flow and integration
The file has no executable logic. `app.js` registers the static loader, and `LocaleService` can select `zh-HK` either from the `lang` query parameter, saved `SYN_LANG`, or browser-language negotiation. `durationFilter.js` treats all Chinese language codes specially by adding `zh_TW` as a humanize-duration fallback; this matters for `zh-HK` because the duration library may not have a dedicated Hong Kong locale.

## State and persistence behavior
The JSON file is static and stateless. The selected locale can be persisted in browser local storage by `LocaleService.useLocale(locale, true)`, but the catalog itself does not write state. Browser/server caching can affect update visibility after translation changes.

## Dependencies and integration points
The catalog depends on angular-translate, the static asset naming convention `lang-<locale>.json`, `valid-langs.js` listing `zh-HK`, and `prettyprint.js` providing its display name. Runtime callers depend on exact key strings and matching placeholders. Because Hong Kong terminology differs from Taiwan terminology, this file is intentionally distinct from `zh-TW` even though `durationFilter.js` may use a `zh_TW` fallback for duration units.

## Risks
The reduced key count creates a higher mixed-language risk. Missing or inconsistent punctuation/placeholder names can make dynamic invite strings awkward or wrong. A translation with embedded angle brackets exists, so sanitization and escaping should be verified for the relevant UI path. Browser language matching in `LocaleService` compares lower-case server-provided accepted languages to lower-case available locales; if the backend provides only `zh` rather than `zh-hk`, it may select the first matching Chinese variant by order instead of this file.

## Test signals
Run JSON validation, compare key coverage against `lang-en.json`, and perform placeholder parity checks. In-browser smoke tests should open `?lang=zh-HK`, verify the language selector label, confirm share invitations interpolate names correctly, and check duration displays for `zh-HK` because that path relies on the Chinese fallback behavior in `durationFilter.js`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-HK.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-TW.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-TW.json

## Purpose
This file is the Taiwan Traditional Chinese (`zh-TW`) angular-translate catalog for the Syncthing default web GUI. It localizes the source English strings used across the AngularJS application and acts as the closest Traditional Chinese fallback for some shared behavior, notably duration formatting for Chinese locales.

## Important APIs, types, and data
The artifact is a JSON object with 546 top-level keys. It contains translations for device and folder management, file synchronization status, ignore rules, versioning, connection/discovery settings, upgrade and restart flows, usage reporting, and common action labels. It includes Angular interpolation placeholders and a nested `theme.name` object mapping theme identifiers to localized labels.

## Control flow and integration
The file has no direct control flow. It is fetched by angular-translate when `$translate.use('zh-TW')` is called by `LocaleService`. `valid-langs.js` makes it selectable, `prettyprint.js` supplies the display name, and `durationFilter.js` adds `zh_TW` as a fallback for all `zh-*` duration-language choices. If a translation key is absent here, the app falls back to English.

## State and persistence behavior
The file is a static JSON resource. Locale persistence is handled outside the file through `LocaleService` and `localStorage.SYN_LANG`; the selected language also updates the root HTML `lang` attribute after `$translate.use()` succeeds.

## Dependencies and integration points
Dependencies are angular-translate JSON loading, exact source-string keys from templates/controllers, the global locale lists, and interpolation compatibility. The nested theme translation data integrates with settings/theme UI where object-valued translation keys can be read by angular-translate or direct code paths.

## Risks
Translation catalogs can drift from the English source when UI strings change. Placeholder mismatches in dynamic folder/device messages would be visible to users. Because `durationFilter.js` uses `zh_TW` as a fallback for Chinese locales, regressions in external humanize-duration language support can affect this locale and `zh-HK`. One value contains angle brackets, so rendering paths should be checked for escaping and correct presentation.

## Test signals
Validate JSON, compare key coverage and placeholder parity against English, load the GUI with `?lang=zh-TW`, check language selector ordering/display, and smoke-test folder/device invite messages and duration values. Also verify `theme.name` still covers every theme identifier used by settings templates.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-TW.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/prettyprint.js -->
# sources/sync-backup/syncthing/gui/default/assets/lang/prettyprint.js

## Purpose
This file defines the global `langPrettyprint` map used by the Syncthing GUI language selector to display human-readable language names for available locale codes.

## Important APIs, types, and functions
The only exported surface is a global variable assignment: `var langPrettyprint = { ... }`. Keys are locale identifiers such as `en`, `pt-BR`, `zh-CN`, `zh-HK`, and `zh-TW`; values are English display names. It is not an ES module or Angular service, so consumers access it as a browser global.

## Control flow and integration
There is no control flow. `LocaleService.getLocalesDisplayNames()` returns this global map, and `languageSelectDirective.js` filters it against `LocaleService.getAvailableLocales()`. The language selector inverts names to codes, sorts by display name, and shows bracketed codes for available locales missing from this map.

## State and persistence behavior
The file is stateless. It affects presentation only; language selection persistence is handled by `LocaleService`.

## Dependencies and integration points
It must be loaded before `LocaleService.getLocalesDisplayNames()` is called. It should stay consistent with `valid-langs.js` and the actual `lang-*.json` assets. Locale codes need exact spelling because they also drive static JSON filenames.

## Risks
Mismatches between `langPrettyprint`, `validLangs`, and catalog files can cause missing selector labels or unselectable translations. Duplicate display names are risky because `languageSelectDirective.js` inverts the map by display name, so later entries with the same name can overwrite earlier locale codes. Because names are sorted as strings, display-name changes affect selector order.

## Test signals
Check that every code in `valid-langs.js` has a corresponding pretty name and a `lang-<code>.json` file, and that no duplicate display names collapse when inverted. Browser smoke testing should confirm the dropdown labels for `zh-CN`, `zh-HK`, and `zh-TW`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/prettyprint.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/valid-langs.js -->
# sources/sync-backup/syncthing/gui/default/assets/lang/valid-langs.js

## Purpose
This file defines the global `validLangs` array of locale codes that the Syncthing GUI considers available for translation and locale selection.

## Important APIs, types, and functions
The only API is the global variable assignment `var validLangs = [...]`. Values are locale strings matching `lang-<code>.json` filenames and `prettyprint.js` keys. `app.js` declares `validLangs` as a global and passes it into `LocaleServiceProvider.setAvailableLocales(validLangs)` during Angular configuration.

## Control flow and integration
The file has no executable logic beyond creating the array. At runtime, `LocaleService` uses this list for browser-language matching and `languageSelectDirective.js` uses it to decide which language names appear in the dropdown. The order can influence automatic browser-language selection when a short accepted language such as `zh` matches multiple available locales.

## State and persistence behavior
The file is static and stateless. It indirectly affects persisted state because users can only choose listed locales for storage in `SYN_LANG` through the language selector, although URL `?lang=` can still request arbitrary language strings and rely on `$translate` behavior.

## Dependencies and integration points
It must be loaded before Angular app configuration in `app.js`. It should be synchronized with actual translation JSON files and `langPrettyprint` display names. The list integrates with `LocaleServiceProvider`, browser locale matching from `/rest/svc/lang`, and the language dropdown.

## Risks
Adding a locale code without a JSON file creates failed translation loads or English fallback. Omitting an existing catalog makes it unreachable from automatic selection and the dropdown. Ordering can affect generic language prefix matches; for example a browser language of `zh` may select the first Chinese variant present in this array.

## Test signals
Validate each `validLangs` entry has both `assets/lang/lang-<code>.json` and a pretty name. Test automatic language negotiation for exact and prefix matches, and verify the dropdown includes all listed languages without bracket fallback labels.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/valid-langs.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/app.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/app.js

## Purpose
This file bootstraps the main AngularJS `syncthing` module and defines shared browser-global utilities used throughout the Syncthing GUI. It wires translation and locale services, configures XSRF header/cookie names, and exposes helper functions for device/folder ordering, object mapping, debouncing, tree-building, and unit-prefix formatting.

## Important APIs, types, and functions
The module declaration creates `angular.module('syncthing', ['angularUtils.directives.dirPagination', 'pascalprecht.translate', 'ngSanitize', 'syncthing.core'])`. Global constants include `urlbase = 'rest'`, `authUrlbase = 'rest/noauth/auth'`, and `shortIDStringLength = 7`. The config block sets angular-translate static files loader prefix/suffix, English fallback, locale provider defaults, async HTTP digest behavior, and metadata-derived CSRF names. Utility functions include `deviceCompare`, `folderCompare`, `deviceMap`, `deviceList`, `folderMap`, `folderList`, `isEmptyObject`, `debounce`, `buildTree`, and `unitPrefixed`.

## Control flow
During Angular config, the app sets translation sanitization to `escape`, registers `assets/lang/lang-*.json`, sets available/default locales, and enables `$httpProvider.useApplyAsync(true)`. If `window.metadata` is missing, setup returns early because unauthenticated pages cannot configure device-specific CSRF names. Device/folder helper functions convert arrays to ID-keyed maps and back with stable sorting. `debounce` invokes immediately on the first call, schedules a trailing call when calls occur within the wait window, and retains the last arguments/context. `buildTree` converts a path-to-data object into a nested tree of folder and file nodes. `unitPrefixed` formats metric or binary quantities up to tera-prefixes using locale-aware number formatting.

## State and persistence behavior
Most helpers are pure except `debounce`, which holds timeout, timestamp, and trailing-call state in closure variables. Angular configuration mutates provider state. CSRF names depend on global `metadata.deviceIDShort`, which comes from the server-rendered page. No local storage is written here, but `LocaleServiceProvider` receives the locale list for later persisted selection.

## Dependencies and integration points
Dependencies include AngularJS, angular-translate, ngSanitize, dirPagination, jQuery, global `validLangs`, browser `metadata`, and Bootstrap-oriented templates/controllers that use the globals. Filters `binaryFilter.js` and `metricFilter.js` call `unitPrefixed`. Controllers use `urlbase`, `authUrlbase`, device/folder map/list helpers, `buildTree` for version restore views, and `shortIDStringLength` for device ID display consistency.

## Risks
Because many utilities are browser globals, load order is critical and refactoring can break filters/controllers without explicit imports. The config early return for missing metadata must preserve unauthenticated login behavior. `deviceCompare` and `folderCompare` return booleans for greater-than cases rather than strictly `1`, relying on JavaScript sort coercion. `buildTree` uses loose equality for folder title comparison and does not sort generated children. `unitPrefixed` only reaches tera units, so very large values remain represented as large tera numbers.

## Test signals
Unit tests should cover sorting by label/name/ID, map/list round trips, debounce leading and trailing calls, path tree construction, and metric/binary formatting at threshold boundaries. Browser tests should verify unauthenticated pages do not require metadata, authenticated requests send the metadata-derived CSRF header/cookie, translations load from the expected paths, and binary/metric filters render locale-aware strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/app.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/alwaysNumberFilter.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/alwaysNumberFilter.js

## Purpose
This AngularJS filter normalizes undefined numeric values to `0` for display paths that should always render a number instead of blank or `undefined`.

## Important APIs, types, and functions
It registers `alwaysNumber` on `syncthing.core`. The returned filter function accepts one input and returns `0` only when `input === undefined`; all other values, including `null`, empty strings, negative numbers, and `NaN`, pass through unchanged.

## Control flow
The filter performs a single strict undefined check and immediate return. There is no async behavior and no dependency injection.

## State and persistence behavior
The filter is stateless and does not persist data.

## Dependencies and integration points
It depends on `syncthing.core` being declared before load. Templates can pipe possibly undefined counters or sizes through `alwaysNumber` before additional formatting.

## Risks
Because only `undefined` is coerced, `null` or `NaN` can still leak to the UI. Combining this filter with numeric formatting filters should account for their handling of non-number inputs.

## Test signals
Template/unit tests should assert `undefined -> 0` and that valid zero, positive, negative, `null`, and string inputs are not modified.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/alwaysNumberFilter.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/basenameFilter.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/basenameFilter.js

## Purpose
This filter extracts the final path component from a slash- or backslash-separated path for display in the Syncthing GUI.

## Important APIs, types, and functions
It registers the `basename` filter on `syncthing.core`. The filter returns an empty string for `undefined`, splits input on both `/` and `\`, and returns the last segment.

## Control flow
The implementation checks for undefined, splits via the regular expression `/[\/\\]/`, guards against an empty `parts` result, and returns the last array entry.

## State and persistence behavior
The filter is pure and stateless.

## Dependencies and integration points
It depends only on Angular module registration. It is useful in templates that display file names from platform-specific paths.

## Risks
Trailing separators return an empty string because the final split segment is empty. Non-string inputs without a `split` method will throw. It does not account for URL paths, Windows drive semantics, or root-only paths beyond simple separator splitting.

## Test signals
Cover Unix paths, Windows paths, paths with trailing separators, undefined input, simple file names, and accidental non-string input if templates may pass model objects.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/basenameFilter.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/binaryFilter.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/binaryFilter.js

## Purpose
This AngularJS filter formats byte-like quantities with binary prefixes for GUI display.

## Important APIs, types, and functions
It registers the `binary` filter on `syncthing.core`. The filter delegates entirely to the global `unitPrefixed(input, true)` helper from `app.js`, which formats using a 1024 factor and suffixes binary units with `i` (`Ki`, `Mi`, `Gi`, `Ti`).

## Control flow
There is no local branching; all formatting control flow lives in `unitPrefixed`.

## State and persistence behavior
The filter is stateless.

## Dependencies and integration points
It requires `unitPrefixed` to exist in global scope before the filter is invoked. Templates likely combine it with size values for files, transfer rates, database sizes, or device statistics.

## Risks
Load-order issues break the filter at runtime because `unitPrefixed` is not injected. Undefined or non-numeric handling follows `unitPrefixed`, which returns `'0 '` for undefined or `NaN`. The filter appends only the prefix, so templates must supply the base unit such as `B` or `/s` where needed.

## Test signals
Check threshold values around 1024, 1024^2, 1024^3, large tera values, undefined, and `NaN`. Browser smoke tests should verify templates append the expected unit text.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/binaryFilter.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/durationFilter.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/durationFilter.js

## Purpose
This AngularJS filter converts a duration in seconds into a compact localized string such as days/hours/minutes/seconds, with caller-controlled precision.

## Important APIs, types, and functions
It registers `duration` on `syncthing.core` and injects `$translate`. The filter signature is `duration(input, precision)`, where `precision` defaults to `"s"` and must be one of `"d"`, `"h"`, `"m"`, or `"s"`. It uses `humanizeDuration(input * 1000, { language, maxDecimalPoints: 0, units, fallbacks })` when a current translation language is available. A local `SECONDS_IN` map powers a manual English-style fallback.

## Control flow
The filter parses `input` as base-10 integer seconds and determines the current language from `$translate.use()`, replacing hyphens with underscores for humanize-duration language codes. For Chinese languages it adds `zh_TW` as a fallback, then adds the base language when the locale is regional, and finally English. It builds the allowed units by popping lower-precision units according to the requested precision. If humanize-duration succeeds, the localized string is returned. If language resolution is absent or humanize-duration throws, it falls back to manual `d h m s` formatting and returns `<1<precision>` for sub-unit values.

## State and persistence behavior
The filter itself is stateless. It reads current translation state from `$translate`, and logs caught humanize-duration errors to `console`.

## Dependencies and integration points
Dependencies are AngularJS, `$translate`, the global `humanizeDuration` library, and the translation locale selected by `LocaleService`. It integrates with locale catalogs indirectly because `$translate.use()` controls its language choice, and with Chinese catalogs through the `zh_TW` fallback rule.

## Risks
Invalid precision returns an error string in the UI. `parseInt` can truncate fractional seconds and turn invalid strings into `NaN`, which can flow to fallback behavior oddly. The manual fallback is not localized and uses compact unit letters only. The `switch` uses fallthrough intentionally, so missing break changes would break precision filtering. If humanize-duration lacks a language and throws, users get English-like output after a console log.

## Test signals
Unit tests should cover all precision values, invalid precision, sub-unit output, zero, fractional or string inputs, Chinese language fallback (`zh-HK` to `zh_TW`), region fallback such as `en_GB` to `en`, and simulated humanize-duration exceptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/durationFilter.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/eventService.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/eventService.js

## Purpose
This AngularJS service maintains the GUI's long-polling connection to Syncthing's REST event stream and broadcasts server events into Angular scope listeners.

## Important APIs, types, and functions
It registers service `Events` on `syncthing.core` and injects `$http`, `$rootScope`, and `$timeout`. Public constants include UI events `ONLINE` and `OFFLINE`, plus many server event type names such as `CONFIG_SAVED`, `DEVICE_CONNECTED`, `DOWNLOAD_PROGRESS`, `FOLDER_SUMMARY`, `ITEM_FINISHED`, `STATE_CHANGED`, and others. The public method `start()` begins polling with `GET rest/events?limit=1`.

## Control flow
`start()` fetches one event to establish `lastID`. `successFn(data)` treats empty data as failure, broadcasts `UIOnline`, broadcasts each returned Syncthing event only after the initial response, updates `lastID` to the last event ID, and immediately starts the next long poll with `GET rest/events?since=<lastID>`. `errorFn(statusString, status)` reloads the page on HTTP 403, broadcasts `UIOffline` for other failures, and schedules a retry after one second using `$timeout(..., false)` to avoid forcing a digest on the timer itself.

## State and persistence behavior
The service keeps `lastID` in closure state for event-stream continuity. It does not persist data across reloads. Online/offline status is distributed as Angular broadcasts rather than stored in the service.

## Dependencies and integration points
It depends on global `urlbase`, Angular's legacy `$http.success/.error` API, `$rootScope` event broadcasting, and the REST `/events` endpoint. Controllers register listeners for the constants or raw server event type names to refresh configuration, folder summaries, device state, progress, and notifications.

## Risks
Using `$http.success/.error` ties the code to AngularJS 1.x legacy APIs. If the first event response contains meaningful events, they are intentionally suppressed by the `lastID > 0` guard. `data.pop()` mutates the response array after broadcasting. A persistent failure creates an infinite retry loop every second. Empty HTTP 200 bodies are correctly treated as failures for restart scenarios, but callers must tolerate offline/online flapping during Syncthing restarts.

## Test signals
Tests should mock `$http` and `$timeout` to verify initial suppression, subsequent event broadcasts, `lastID` advancement, empty-success fallback to offline retry, 403 reload behavior, and retry URL selection. Integration tests should confirm controllers receive expected broadcasts from real `/rest/events` traffic.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/eventService.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/identiconDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/identiconDirective.js

## Purpose
This directive renders a deterministic SVG identicon for a supplied value, typically a device ID or other stable identifier shown in the Syncthing GUI.

## Important APIs, types, and functions
It registers an element directive `identicon` with isolate scope `{ value: '=' }`. The inner `Identicon(value, size)` function creates an SVG in the SVG namespace, defaults to a 5x5 grid, and fills mirrored rectangles based on the parity of character codes from the sanitized value.

## Control flow
The directive link function appends a newly constructed `Identicon(scope.value)` to the element once. `Identicon` removes non-word and underscore characters from the value, iterates rows and the left/middle columns, fills a rectangle when `value.charCodeAt(row + col * size)` is even, and mirrors filled rectangles across the vertical axis except for the center column in odd-size grids.

## State and persistence behavior
The directive is stateless after initial render and does not watch `value` for later changes. It does not persist data.

## Dependencies and integration points
Dependencies are AngularJS, the browser DOM/SVG APIs, and `$window.parseInt`. CSS class `identicon` controls visual styling such as fill color. Templates use `<identicon value="...">` where the value is expected to be stable before linking.

## Risks
If `value` changes after link, the SVG remains stale. For short sanitized values, `charCodeAt` can return `NaN`, and `$window.parseInt(NaN, 10) % 2` leads to no fill for those cells. Identicons are not cryptographic; collisions and visually sparse icons are possible. Appending directly without clearing can duplicate SVGs if the directive is re-linked on reused DOM.

## Test signals
Tests should render known values and assert deterministic SVG rectangle positions, symmetry, empty-value behavior, and non-updating behavior when scope value changes. Visual smoke tests should confirm CSS makes the generated SVG visible at intended sizes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/identiconDirective.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/languageSelectDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/languageSelectDirective.js

## Purpose
This directive renders the language selector dropdown and connects user language changes to `LocaleService`.

## Important APIs, types, and functions
It registers `languageSelect` as element/attribute directive. Its inline template renders a Bootstrap dropdown with a globe icon, current locale display name, and one menu item per available locale. The link function reads `LocaleService.getAvailableLocales()`, `getLocalesDisplayNames()`, `getCurrentLocale()`, and calls `LocaleService.useLocale(locale, true)` when the user selects a language.

## Control flow
The directive filters display names to locales that are actually available, falling back to `[code]` labels when a pretty name is missing. It inverts the code-to-name object into name-to-code, sorts names alphabetically, and shows the dropdown only when English is present. A `$watch` waits for `LocaleService.getCurrentLocale` to become truthy because `LocaleService.autoConfigLocale()` may select a locale asynchronously after `/svc/lang`; once found, it sets `$scope.currentLocale` and removes the watcher. `changeLanguage()` persists the selected locale and updates the local current-locale state.

## State and persistence behavior
Directive scope stores `localesNames`, inverted maps, sorted names, `visible`, and `currentLocale`. Persistence is delegated to `LocaleService.useLocale(locale, true)`, which writes `SYN_LANG` when local storage is available.

## Dependencies and integration points
It depends on Bootstrap dropdown markup/classes, Font Awesome globe icon classes, `LocaleService`, global locale metadata consumed by that service, and Angular scope watching. It integrates with `prettyprint.js` and `valid-langs.js` through the service provider configuration.

## Risks
Inverting by display name loses entries when two locales share the same display name. The initial watcher removes itself on the first truthy current locale, so external later changes must also update `$scope.currentLocale` through `changeLanguage()` or re-render. Missing English hides the selector. The template uses `href="#"`; click handlers rely on Angular/Bootstrap behavior to avoid unwanted navigation.

## Test signals
Unit tests should cover missing pretty names, duplicate display names, initial async locale selection, `changeLanguage()` persistence calls, and visibility when `en` is absent. Browser tests should verify dropdown ordering, active class assignment, and selected locale display.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/languageSelectDirective.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/localeNumberFilter.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/localeNumberFilter.js

## Purpose
This filter formats a number using the browser's current locale-aware `toLocaleString()` behavior.

## Important APIs, types, and functions
It registers `localeNumber` on `syncthing.core`. The returned function calls `input.toLocaleString()` with no explicit locale or options.

## Control flow
There is no branching; input is expected to provide a `toLocaleString` method.

## State and persistence behavior
The filter is stateless. Output depends on browser locale/runtime settings, not app-managed persistence.

## Dependencies and integration points
It depends on JavaScript's built-in `toLocaleString`. Templates use it for user-facing numeric values where grouping and decimal separators should follow browser defaults.

## Risks
`undefined` or `null` inputs throw because the filter does not guard them. Output can vary by browser and user locale, which may make tests brittle. It does not necessarily align with the selected GUI translation language because no explicit locale is passed.

## Test signals
Tests should include normal numbers, large numbers, decimal values, and guarded calling contexts for undefined/null. Prefer assertions on method invocation or broad formatting shape over exact separators unless locale is fixed.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/localeNumberFilter.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/localeService.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/localeService.js

## Purpose
This provider owns GUI locale selection for Syncthing: available/default locale configuration during app bootstrap, automatic locale detection, explicit locale changes, translation activation, HTML language attribute updates, and optional persistence in local storage.

## Important APIs, types, and functions
The provider exposes `setDefaultLocale(locale)` and `setAvailableLocales(locales)` during config. The runtime service exposes `autoConfigLocale()`, `useLocale(language, save2Storage)`, `getCurrentLocale()`, `getAvailableLocales()`, and `getLocalesDisplayNames()`. Internal helpers include `detectLocalStorage()`, `readBrowserLocales()`, and `autoConfigLocale()`'s matching loop. The storage key is the constant string `SYN_LANG`.

## Control flow
Provider construction feature-detects `window.localStorage` by writing and removing a temporary key. `autoConfigLocale()` first checks `$location.search().lang`; if present, it immediately uses and persists that locale. Otherwise it checks saved `SYN_LANG`; if present, it uses it without rewriting. If neither exists, it calls `GET rest/svc/lang` and scans the returned browser-language preferences. For each language, it finds available locales whose lower-case code starts with the browser language and either exactly matches or has a hyphen separator after the prefix. The first match wins; otherwise the configured default locale is used. `useLocale()` calls `$translate.use(language).then(...)`, sets `document.documentElement.lang`, and writes `SYN_LANG` when requested and storage is available.

## State and persistence behavior
Provider-level state holds `_defaultLocale`, `_availableLocales`, and `_localStorage`. Runtime state is mostly managed by `$translate`; this service reads from and writes to that state. Persistent browser state is optional `localStorage.SYN_LANG`. The root document `lang` attribute is mutable UI/document state and updates only after translation loading succeeds.

## Dependencies and integration points
Dependencies include `$http`, `$translate`, `$location`, global `urlbase`, global `langPrettyprint`, browser `window.localStorage`, and `document.documentElement`. `app.js` configures available/default locales. `languageSelectDirective.js` reads current/available/display names and calls `useLocale()`. `durationFilter.js` reads `$translate.use()` separately, so locale selection here influences duration formatting.

## Risks
URL `?lang=` accepts any string and passes it to `$translate.use`; missing catalog behavior depends on angular-translate fallback/loading errors. The browser-language match depends on order in `valid-langs.js`, so generic prefixes can select an unintended regional variant. Local-storage access can be unavailable and is correctly guarded, but persistence silently disappears in private/restricted environments. Since `useLocale()` writes storage only after `$translate.use()` resolves, failed catalog loads do not persist but may leave the current locale unchanged.

## Test signals
Mock `$http`, `$translate`, `$location`, and localStorage to cover precedence order (`?lang`, saved value, browser list, default), prefix matching boundaries, unavailable storage, successful persistence, root `lang` attribute updates, and missing/failed language loads. Integration tests should verify `rest/svc/lang` negotiation and language selector changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/localeService.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/metricFilter.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/metricFilter.js

## Purpose
This AngularJS filter formats numeric quantities with decimal metric prefixes for GUI display.

## Important APIs, types, and functions
It registers `metric` on `syncthing.core`. The filter delegates to global `unitPrefixed(input, false)`, using a factor of 1000 and suffixes such as `k`, `M`, `G`, and `T`.

## Control flow
The filter has no local branching. All threshold and locale-aware formatting logic resides in `app.js`'s `unitPrefixed`.

## State and persistence behavior
The filter is stateless.

## Dependencies and integration points
It requires `unitPrefixed` in global scope and Angular module initialization. Templates use it for rates or counts where decimal SI-style formatting is desired.

## Risks
Load-order coupling to a global helper is implicit. Undefined or invalid values become `'0 '`, and the filter returns a prefix-bearing number without the base unit. Very large values are expressed as large tera values because no peta prefix is implemented.

## Test signals
Cover threshold boundaries around 1000, 1e6, 1e9, 1e12, undefined, `NaN`, and locale effects. Template smoke tests should confirm surrounding unit text is correct.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/metricFilter.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/modalDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/modalDirective.js

## Purpose
This directive wraps Syncthing's Bootstrap modal template and adds behavior needed for nested/stacked modals, tab links inside modals, modal backdrop z-index management, body scroll restoration, and controller notification when a modal has loaded.

## Important APIs, types, and functions
It registers element directive `modal` on `syncthing.core`. The directive uses `templateUrl: 'modal.html'`, `replace: true`, `transclude: true`, and an isolate scope with string attributes `heading`, `status`, `icon`, `closeable`, and `large`. Its link function installs jQuery/Bootstrap event handlers for click, `show.bs.modal`, `hide.bs.modal`, and `hidden.bs.modal`, and calls `scope.$parent.modalLoaded()`.

## Control flow
Click handling intercepts tab anchors (`a[data-toggle="tab"]`) with hash hrefs and prevents default navigation. On show, the directive finds the highest z-index among visible modals, places the current modal above it, and after a zero-delay timeout adjusts the latest backdrop and hides older backdrops visually. On hide, it finds the next highest backdrop not associated with the closing modal and restores its visible class. On hidden, it resets the modal z-index and re-adds `modal-open` to the body if other modals remain visible. Finally, link-time calls `modalLoaded()` on the parent scope so the controller can track readiness.

## State and persistence behavior
The directive mutates DOM state: modal z-index, backdrop classes/attributes, and body classes. It does not persist application data. It depends on parent-scope state indirectly through `modalLoaded()`.

## Dependencies and integration points
Dependencies are AngularJS, jQuery, Bootstrap modal/backdrop markup/events, `modal.html`, parent controllers implementing `modalLoaded`, and templates that rely on this directive's isolate/transcluded scope composition. The inline comment warns that templates may rely on `$parent.$parent`, so scope shape is a compatibility concern.

## Risks
DOM event handlers are not explicitly removed on scope destruction, which can matter if modals are dynamically created/destroyed. Stacked modal behavior relies on Bootstrap class names and z-index defaults. Calling `scope.$parent.modalLoaded()` will throw if the parent does not provide that function. The directive uses `event.target.closest`, so very old browsers without `Element.closest` need polyfill support.

## Test signals
Browser tests should open stacked modals, close inner and outer modals, confirm backdrop visibility and body scrolling, exercise tab links inside modals, and verify parent `modalLoaded()` is called. Unit tests can mock jQuery events, but integration tests with Bootstrap are more valuable.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/modalDirective.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/module.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/module.js

## Purpose
This file declares the AngularJS `syncthing.core` module that hosts shared Syncthing GUI services, filters, and directives.

## Important APIs, types, and functions
The only API is `angular.module('syncthing.core', []);`, creating the module with no Angular module dependencies.

## Control flow
There is no runtime branching. The declaration must execute before files that call `angular.module('syncthing.core')` to register components.

## State and persistence behavior
The Angular module registry is mutated by this declaration. No application state is persisted.

## Dependencies and integration points
It depends on AngularJS being loaded. `app.js` depends on this module by listing `'syncthing.core'` in the main `syncthing` module dependencies. All core files in this subset register against this module.

## Risks
Load order is critical: if registration files load before this declaration, Angular throws "module not available"; if this declaration runs after registrations, it recreates the module and discards previously registered components. Any future dependencies must be added here carefully.

## Test signals
Bundle/order tests should ensure `module.js` precedes core component registrations and `app.js` can bootstrap the main module. A simple Angular injector smoke test can assert registered filters/services/directives are available.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/module.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/notificationDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/notificationDirective.js

## Purpose
This directive conditionally displays notification content when its notification ID is present in the current Syncthing configuration's unacknowledged notification list.

## Important APIs, types, and functions
It registers element directive `notification` on `syncthing.core`. The directive has an empty isolate scope, transcludes inner content, and uses template `<div class="row" ng-if="visible()"><div class="col-md-12" ng-transclude></div></div>`. The link function defines `scope.visible()` by checking `scope.$parent.config.options.unackedNotificationIDs.indexOf(attrs.id) > -1`.

## Control flow
On each digest where `visible()` is evaluated, the directive reads parent configuration and returns true when the directive's `id` attribute is in the unacknowledged list. Angular `ng-if` creates or removes the transcluded content accordingly.

## State and persistence behavior
The directive does not own state. It reflects parent configuration state. Acknowledgement and persistence of notifications happen elsewhere in controller/API code.

## Dependencies and integration points
It depends on parent scope shape: `config.options.unackedNotificationIDs` must exist and be an array. It integrates with notification templates and the controller that loads/saves Syncthing configuration.

## Risks
If config or options are unavailable during early render, `visible()` can throw. Missing `id` attributes will check for `undefined` in the array. Because it uses isolate scope but reaches into `$parent`, template relocation can break it.

## Test signals
Tests should cover visible and hidden states, missing IDs, dynamic updates to `unackedNotificationIDs`, and initial loading states where config may not yet be populated.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/notificationDirective.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/pathIsSubDirDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/pathIsSubDirDirective.js

## Purpose
This directive adds Angular model validation-side effects for folder path forms, detecting whether the current folder path is a subdirectory of another configured folder or a parent of another configured folder.

## Important APIs, types, and functions
It registers attribute directive `pathIsSubDir` requiring `ngModel`. The directive adds `ctrl.$validators.folderPathErrors = function(viewValue) { ... }`. Inside, helper `isSubDir(xdir, ydir)` normalizes leading `~` using `scope.system.tilde` and `scope.system.pathSeparator`, splits paths, trims a trailing empty segment from `xdir`, and checks whether all `xdir` path components match the corresponding prefix of `ydir`.

## Control flow
For each validation run, it resets `scope.folderPathErrors` flags and metadata, returns true immediately for empty input, then iterates every folder in `scope.folders` except `scope.currentFolder.id`. If an existing folder path is a prefix of the new value, it marks `isSub`; if the new value is a prefix of an existing folder path, it marks `isParent`. It records the other folder's ID and label and breaks after the first match. The validator always returns true, so it does not invalidate the field; it only populates warning/error state for the template.

## State and persistence behavior
The directive mutates `scope.folderPathErrors` on the parent/current scope. It does not persist data or block saving directly through Angular validity.

## Dependencies and integration points
It depends on `ngModel`, `scope.system.pathSeparator`, `scope.system.tilde`, `scope.folders`, `scope.currentFolder`, and `scope.folderPathErrors`. It integrates with edit-folder templates that display subdirectory/parent-directory warnings and with controller-provided folder maps.

## Risks
Because the validator always returns true, any prevention must happen elsewhere; otherwise this is advisory only. Path comparison is string/component based and does not resolve symlinks, relative paths, case-insensitive filesystems, `.`/`..`, or Windows drive normalization beyond separator splitting. The tilde expansion regex uses template literals and assumes modern JavaScript support. It trims only `xdir` trailing separators, not `ydir`, which may affect equality and trailing-separator cases.

## Test signals
Tests should cover subdirectory, parent-directory, equal paths, trailing separators, tilde expansion, current-folder exclusion, Windows and Unix separators, empty input, and advisory return value behavior. UI tests should verify the correct other folder ID/label appears.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/pathIsSubDirDirective.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/percentFilter.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/percentFilter.js

## Purpose
This filter formats numeric percentage values for compact display in the Syncthing GUI.

## Important APIs, types, and functions
It registers `percent` on `syncthing.core`. The filter returns `'0%'` for undefined values or values below `0.01`, uses `toLocaleString(undefined, { maximumFractionDigits: 2 })` for values below `0.1`, and otherwise uses `toLocaleString(undefined, { maximumSignificantDigits: 2 })`, always appending `%`.

## Control flow
The control flow is a three-branch threshold formatter: suppress tiny values to zero, preserve up to two decimal places for very small non-zero percentages, and use two significant digits for the rest.

## State and persistence behavior
The filter is stateless. Output depends on browser locale formatting.

## Dependencies and integration points
It depends only on JavaScript `Number.toLocaleString` and Angular filter registration. Templates use it for completion, progress, and possibly error/rate percentages.

## Risks
`null`, strings, or `NaN` are not explicitly guarded and may produce surprising output or throw depending on the type. Locale output varies by browser. Inputs are assumed to already be in percent units, not fractions; passing `0.5` renders `0.5%`, not `50%`.

## Test signals
Cover undefined, zero, below `0.01`, between `0.01` and `0.1`, normal values, values over 100, `NaN`, and string inputs if template data may not be numeric.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/percentFilter.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/popoverDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/popoverDirective.js

## Purpose
This directive initializes Bootstrap popovers on elements that declare the `popover` attribute.

## Important APIs, types, and functions
It registers attribute directive `popover` on `syncthing.core`. The link function calls `$(element).popover()`.

## Control flow
There is no branching. Initialization occurs once when Angular links the element.

## State and persistence behavior
The directive creates Bootstrap/jQuery plugin state attached to the DOM element. It does not persist application data and does not explicitly destroy popover state on scope teardown.

## Dependencies and integration points
Dependencies are AngularJS, jQuery, Bootstrap's popover plugin, and markup attributes consumed by Bootstrap such as title, content, placement, trigger, or data attributes. It integrates with templates that need hover/click contextual help.

## Risks
If Bootstrap's popover plugin is not loaded, `$(element).popover` is undefined. Dynamic content changes after initialization may not update unless Bootstrap is configured accordingly. Missing destroy cleanup can leave event handlers on frequently recreated elements.

## Test signals
Browser tests should confirm popovers initialize and display with expected content and placement. Unit tests can stub `$.fn.popover` and assert it is called once per linked element; teardown behavior should be considered if elements are dynamic.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/popoverDirective.js -->
