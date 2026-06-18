# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/swagger-ui-bundle.js lines 21-21

## Scope And Purpose

This chunk covers the final line of the generated Swagger UI bundle vendored into the Ozone documentation theme:

`//# sourceMappingURL=swagger-ui-bundle.js.map`

The line is a JavaScript source map directive. It does not execute application logic, but it tells browsers and developer tools that the minified bundle can be mapped back to a `swagger-ui-bundle.js.map` companion file. The surrounding file is otherwise a generated/minified Swagger UI browser bundle with an Apache header, a license sidecar notice, a UMD wrapper exporting `SwaggerUIBundle`, and a large webpack module table on line 20. The source map directive is therefore a build/debug metadata hook for that generated asset, not part of the Ozone runtime Java or server code.

The file is used by the Ozone docs Swagger shortcode at `hadoop-hdds/docs/themes/ozonedoc/layouts/shortcodes/swagger-ui.html`, which loads `/swagger-resources/swagger-ui-bundle.js`, loads `swagger-ui-standalone-preset.js`, and initializes `SwaggerUIBundle` against the Recon API YAML. This makes the directive relevant to browser-side debugging of the generated Recon API page.

## Important APIs, Types, And Functions In The Referenced Bundle

Although line 21 itself only names the missing map file, the directive belongs to the bundle that exposes the public `SwaggerUIBundle` factory. The generated UMD wrapper on the preceding line supports CommonJS (`module.exports`), AMD (`define`), generic `exports`, and browser global (`this.SwaggerUIBundle`) consumers.

The bundle contains Swagger UI 5.4.2 metadata embedded near the factory tail:

- `PACKAGE_VERSION: "5.4.2"`
- `GIT_COMMIT: "g6aa1b445"`
- `GIT_DIRTY: true`
- `BUILD_TIME: "Thu, 17 Aug 2023 19:08:57 GMT"`

The main initializer function builds a Swagger UI system from default configuration, query-derived configuration when enabled, presets, plugins, initial state, and user overrides. Its exported static fields include `SwaggerUIBundle.presets.apis` and `SwaggerUIBundle.plugins`, both consumed by the local Hugo shortcode.

Visible bundle components and helpers include:

- Model rendering components for object, array, primitive, enum, collapsed model, and schema property views.
- Operation, response, parameter, request body, content type, Try It Out, execute, authorization, and error components.
- `BaseLayout`, `VersionPragmaFilter`, SVG asset definitions, markdown rendering, examples selection, deep links, and Swagger/OpenAPI version validation UI.
- JSON-schema form controls for strings, arrays, booleans, files, enums, text areas, validation error display, and array item add/remove behavior.
- URL sanitization helpers that reject dangerous protocols such as `javascript:`, `data:`, and `vbscript` by returning `about:blank`.
- Online validator badge support using the default `https://validator.swagger.io/validator` endpoint when `validatorUrl` is not overridden.

The local shortcode configures the public API as:

- `url: "{{ .Get "url" }}"`, with the Ozone Recon page passing `../swagger-resources/recon-api.yaml`.
- `dom_id: '#api-container'`.
- `deepLinking: true`.
- `presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset]`.
- `plugins: [SwaggerUIBundle.plugins.DownloadUrl]`.
- `layout: "StandaloneLayout"`.
- `docExpansion: 'none'`.

## Control Flow

Line 21 has no control flow. Browser developer tools parse it after loading the script and may then request `swagger-ui-bundle.js.map` relative to the bundle URL. If the map is present, stack traces, breakpoints, and inspected sources can be mapped back to original webpack module/source paths. If it is absent, runtime behavior is unchanged, but developer tools typically show a failed map fetch or a warning.

The executable line immediately before it performs the actual runtime flow:

1. The UMD wrapper detects the module environment and publishes `SwaggerUIBundle`.
2. The internal webpack bootstrap resolves bundled modules and returns the default export.
3. The exported factory merges default Swagger UI options with caller options and optional query-string config.
4. It creates and registers the Swagger UI system, plugins, components, functions, and state.
5. It loads a remote config when configured, or directly applies config and downloads the API definition URL.
6. It renders the configured layout into either `domNode` or a DOM element selected by `dom_id`.

For Ozone docs, the shortcode's `window.onload` invokes this flow after the generated page is loaded. The source map directive participates only after script load, and only for tooling.

## State And Persistence Behavior

The directive itself does not read or mutate state and does not persist anything. Its only observable side effect is an optional browser/devtools fetch for `swagger-ui-bundle.js.map`.

The containing bundle initializes in-memory Swagger UI application state, including layout, filter state, spec URL/spec string, request snippet settings, configs, and plugin-provided slices. Defaults visible in the minified initializer include:

- `persistAuthorization: false`, so credentials are not persisted by default.
- `queryConfigEnabled: false`, so query-string configuration is ignored unless explicitly enabled.
- `deepLinking: false` by default, overridden to `true` by the Ozone shortcode.
- `tryItOutEnabled: false` by default.
- `requestInterceptor` and `responseInterceptor` identity functions.
- `supportedSubmitMethods` covering common HTTP methods.

Because the local shortcode does not enable persisted authorization, the docs page should not retain API auth material across reloads through Swagger UI's persistence path. Any downloaded OpenAPI spec and UI state are browser-memory runtime state for the page.

## Dependencies And Generated-Asset Composition

This is a vendored/generated browser artifact, not source-authored application code. The minified bundle includes React-style component definitions, Immutable-style data access, Swagger UI core plugins, URL parsing/sanitization utilities, markdown/autolink handling, syntax highlighting configuration, request/response UI, schema rendering, authorization UI, and webpack runtime glue.

The source map line depends on a sidecar file named `swagger-ui-bundle.js.map` being served from the same `/swagger-resources/` directory. In this checkout, the directory contains `recon-api.yaml`, favicons, `swagger-ui-bundle.js`, `swagger-ui-standalone-preset.js`, and `swagger-ui.css`; the referenced `.map` file is not present. The file also contains a license notice pointing to `swagger-ui-bundle.js.LICENSE.txt`, and that sidecar is likewise not present in the same directory.

## Integration Points

The bundle is integrated into the Ozone docs theme through static assets and Hugo shortcodes:

- `hadoop-hdds/docs/themes/ozonedoc/layouts/partials/header.html` includes `/swagger-resources/swagger-ui.css`.
- `hadoop-hdds/docs/themes/ozonedoc/layouts/shortcodes/swagger-ui.html` loads this bundle and the standalone preset.
- `hadoop-hdds/docs/content/interface/SwaggerReconApi.md` invokes the shortcode with `../swagger-resources/recon-api.yaml`.
- The static asset directory serves `recon-api.yaml` beside the Swagger UI JavaScript and CSS.

Line 21 specifically integrates with browser developer tooling and source-map consumers. It is not consumed by Hugo, Ozone services, or the Swagger UI factory at runtime.

## Risks And Maintenance Notes

The most direct risk in this chunk is metadata drift: the bundle advertises `swagger-ui-bundle.js.map`, but the map file is absent from the static resource directory. This does not break the docs UI, but it creates noisy browser devtools warnings and makes debugging minified Swagger UI issues harder.

The missing license sidecar referenced by line 19 is adjacent to this concern. Since the bundle says license information is in `swagger-ui-bundle.js.LICENSE.txt`, packaging should either include that generated sidecar or remove/update the notice in a compliant way when the asset is refreshed.

Because this file is a minified third-party/generated dependency, manual edits to line 20 or line 21 are brittle. Future maintenance should prefer replacing the Swagger UI distribution as a coherent set: bundle, standalone preset, CSS, source maps if desired, and generated license sidecars. Updating only one generated asset can create version skew between `SwaggerUIBundle`, `SwaggerUIStandalonePreset`, CSS class expectations, and license/debug metadata.

The bundle's default online validator endpoint can cause browser requests to `validator.swagger.io` when the validator badge path is active and a remote URL is used. That is not caused by line 21, but it is a relevant browser-side integration risk for documentation pages in offline or privacy-sensitive environments.

The shortcode's `dom_id` is `#api-container`, while the same template defines `<div id="swagger-ui"></div>`. Rendering still depends on the final generated page having an `api-container` element from elsewhere or this is a latent integration mismatch. This bundle's initializer logs a skipped-rendering error only when neither `dom_id` nor `domNode` is configured; a selector that does not match could still lead to an empty Swagger UI mount depending on Swagger UI's render implementation.

## Test Signals

Useful validation signals for this chunk are browser/static-asset checks rather than unit tests:

- Build or serve the Ozone docs page containing `SwaggerReconApi.md` and verify that `SwaggerUIBundle` initializes and renders the Recon API definition from `recon-api.yaml`.
- In browser devtools, confirm whether `swagger-ui-bundle.js.map` is requested and returns 404; this validates the current source-map metadata mismatch.
- Check the network panel for `swagger-ui-bundle.js`, `swagger-ui-standalone-preset.js`, `swagger-ui.css`, and `recon-api.yaml` all returning successful responses.
- Confirm the rendered page does not rely on source maps for normal operation; disabling devtools/source maps should not change UI behavior.
- If the static distribution is refreshed, verify that the source map directive, `.map` file, and license sidecar files are internally consistent with the shipped bundle version.
