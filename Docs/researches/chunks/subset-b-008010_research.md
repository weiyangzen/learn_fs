# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/swagger-ui-bundle.js lines 20-20

## Purpose

This chunk is the complete executable payload of Ozone's vendored Swagger UI bundle. Lines 1-19 are the Apache header and webpack license pointer; line 20 contains the minified UMD wrapper and all bundled JavaScript. The wrapper publishes a `SwaggerUIBundle` factory through CommonJS, AMD, `exports`, or the browser global, so the same artifact can run in a static browser page and in module-aware environments.

In this source tree the browser-global path is the active integration path. `themes/ozonedoc/layouts/shortcodes/swagger-ui.html` loads `/swagger-resources/swagger-ui-bundle.js`, then calls `SwaggerUIBundle({...})` to render the Recon OpenAPI document from `../swagger-resources/recon-api.yaml` into `#api-container`. The file is therefore documentation UI infrastructure, not Ozone service runtime code.

## Important APIs, Types, And Functions

- `SwaggerUIBundle(options)` is the public entry point exported by the UMD wrapper. It builds the Swagger UI system, registers presets/plugins, loads local or remote specs, and renders the configured React layout.
- `SwaggerUIBundle.presets.apis` exposes the API documentation preset assembled by the bundle. Ozone's shortcode combines it with `SwaggerUIStandalonePreset` from `swagger-ui-standalone-preset.js`.
- `SwaggerUIBundle.plugins` exposes bundled plugin modules, including the `DownloadUrl` plugin used by the shortcode.
- The build metadata embedded in the payload identifies Swagger UI `PACKAGE_VERSION: "5.4.2"`, `GIT_COMMIT: "g6aa1b445"`, `GIT_DIRTY: true`, and `BUILD_TIME: "Thu, 17 Aug 2023 19:08:57 GMT"`. At initialization this is stored under `versions.swaggerUi` in the Swagger client/system object.
- The initialization defaults include `layout: "BaseLayout"`, `docExpansion: "list"`, `validatorUrl: "https://validator.swagger.io/validator"`, `deepLinking: false`, `tryItOutEnabled: false`, `persistAuthorization: false`, `defaultModelRendering: "example"`, model expansion depths of `1`, `supportedSubmitMethods` for the standard HTTP methods, and `syntaxHighlight` using the `agate` theme.
- The bundle registers many React components by name, including authorization controls, API info, operations, parameters, responses, model rendering, examples, markdown rendering, filters, schemes/servers, webhooks, version guards, and SVG assets.
- The bundle contains schema and model components for Swagger 2.0, OpenAPI 3.0, and OpenAPI 3.1/JSON Schema 2020-12 rendering. The visible version guard reports invalid documents when both `swagger` and `openapi` fields are present or when no supported version field exists.
- URL safety helpers sanitize dangerous schemes such as `javascript:`, `data:`, and `vbscript:` to `about:blank` before rendering external links.
- The online validator badge component builds validator URLs from the configured API definition URL and only renders when the validator and definition URLs pass URL validation.

## Control Flow

The line begins with a webpack UMD bootstrap. It chooses the export target, invokes the bundled module loader, and returns the default export as `SwaggerUIBundle`.

The public factory constructs a default configuration object, optionally overlays query-string configuration when `queryConfigEnabled` is true, merges caller options, and creates an initial Swagger UI system state with layout, filter, spec URL/spec text, and request snippet configuration. It registers the configured presets and plugins, obtains the runtime system, then applies the final configs.

Spec loading branches on the supplied options:

- If an inline `spec` object is present and no query URL overrides it, the spec is serialized into the state and loading status is marked successful.
- If `url` is present and `urls` is absent, `specActions.download(url)` fetches the OpenAPI/Swagger definition.
- If a remote config URL is supplied, the bundle first calls `getConfigByUrl`, then continues initialization through the same render callback.

Rendering targets either an explicit `domNode` or a CSS selector in `dom_id`. Ozone passes `dom_id: "#api-container"` from the Hugo shortcode, so the bundle queries that element and renders the configured application layout there. The shortcode overrides defaults with `deepLinking: true`, `layout: "StandaloneLayout"`, and `docExpansion: "none"`.

## State And Persistence Behavior

Runtime state is held in the Swagger UI system store created inside the factory call. Important state slices include loaded configs, layout/filter state, spec content and URL, request snippets, authorization state, operation expansion, parameter/body form values, response data, and errors.

By default this bundle does not persist credentials because `persistAuthorization` is false. The caller may enable persistence, but Ozone's shortcode does not. The only durable inputs in this tree are the static JavaScript/CSS assets and `recon-api.yaml`; the UI state is rebuilt on page load. The shortcode assigns the returned system to `window.ui`, which makes the live UI inspectable from browser developer tools but does not persist it across navigation.

## Dependencies And Integration Points

This minified payload includes bundled copies of Swagger UI's frontend dependencies, including React component code, immutable data handling, markdown/autolink rendering, URL parsing/sanitization helpers, OpenAPI/Swagger parsing and rendering logic, syntax highlighting support, request execution plumbing, and plugin/preset infrastructure.

Local integration points are:

- `themes/ozonedoc/layouts/shortcodes/swagger-ui.html`, which loads this bundle and invokes `SwaggerUIBundle`.
- `themes/ozonedoc/static/swagger-resources/swagger-ui-standalone-preset.js`, which supplies the standalone preset used beside `SwaggerUIBundle.presets.apis`.
- `themes/ozonedoc/static/swagger-resources/swagger-ui.css`, included from `layouts/partials/header.html` after Ozone's CSS to style the rendered UI.
- `themes/ozonedoc/static/swagger-resources/recon-api.yaml`, the API definition passed by `docs/content/interface/SwaggerReconApi.md`.
- `layouts/custompage/swagger-page.html`, which provides the `#api-container` render target.

The bundle also has optional external integration with `https://validator.swagger.io/validator` for the online validator badge and with any configured API server when "try it out" execution is enabled by configuration.

## Risks And Maintenance Notes

- The file is a large vendored, minified, single-line artifact. Local edits are impractical and should generally be made by updating the upstream Swagger UI version and replacing the generated assets together.
- The bundle is versioned as Swagger UI 5.4.2 from August 2023. Security or compatibility fixes in later Swagger UI releases will not be present until this vendored asset is refreshed.
- The payload references `swagger-ui-bundle.js.LICENSE.txt` and `swagger-ui-bundle.js.map`, but this static directory only contains `swagger-ui-bundle.js`; missing license/source-map companions reduce auditability and browser debugging quality.
- Because the bundle runs in the documentation origin, any vulnerability in Markdown rendering, URL sanitization, request execution, or OAuth handling can affect readers of the generated Ozone docs.
- The default validator URL points to an external service. Ozone's shortcode does not override it, so documentation pages may contact `validator.swagger.io` when the validator badge path is active for URL-loaded specs.
- The shortcode creates an unused `<div id="swagger-ui"></div>` while rendering into `#api-container`; the actual render target depends on the surrounding `swagger-page.html` layout.
- `tryItOutEnabled` defaults to false, but Swagger UI still includes request execution code and supported submit methods. Future shortcode/config changes could make the static docs send live requests to configured API endpoints.

## Test Signals

The strongest source-tree signal is a documentation build and browser smoke test for `docs/content/interface/SwaggerReconApi.md`: the generated page should load `swagger-ui-bundle.js`, `swagger-ui-standalone-preset.js`, `swagger-ui.css`, and `recon-api.yaml`; create `window.ui`; render into `#api-container`; show the Recon API operations; and honor deep links with collapsed operations by default.

Useful regression checks include confirming that the browser console has no `SwaggerUIBundle is not defined` or missing render-target errors, that `/swagger-resources/recon-api.yaml` downloads successfully from the generated site, and that the static asset set remains internally consistent when refreshing the vendored Swagger UI files.
