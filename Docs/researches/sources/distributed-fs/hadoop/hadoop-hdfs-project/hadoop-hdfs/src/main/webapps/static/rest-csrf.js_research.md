# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/rest-csrf.js

## Purpose
This Hadoop-specific browser script configures client-side CSRF protection for WebHDFS REST requests. It reads NameNode configuration from `/conf`, determines whether WebHDFS CSRF protection is enabled, and if so installs a jQuery global AJAX `beforeSend` hook that adds the configured custom header to protected `/webhdfs/` requests.

## Important APIs, Types, and Functions
- The file is an immediately invoked function expression with `"use strict"` and no exported public API.
- Closure state includes `restCsrfCustomHeader` and `restCsrfMethodsToIgnore`, initially `null`.
- A synchronous `$.ajax({ url: '/conf', dataType: 'xml', async: false })` fetch reads the NameNode XML configuration before subsequent scripts issue WebHDFS calls.
- Local helpers `getBooleanValue(element)`, `getTrimmedStringValue(element)`, and `getTrimmedStringArrayValue(element)` parse property values from XML.
- The script recognizes `dfs.webhdfs.rest-csrf.enabled`, `dfs.webhdfs.rest-csrf.custom-header`, and `dfs.webhdfs.rest-csrf.methods-to-ignore`.
- `addRestCsrfCustomHeader(xhr, settings)` is the installed callback. It checks the URL prefix, request method, configured header name, and ignored-method map before calling `xhr.setRequestHeader(restCsrfCustomHeader, '""')`.

## Control Flow
On load, the script requests `/conf` synchronously. In the success callback, it iterates all `<property>` elements, extracts the three CSRF-related settings, and if CSRF is enabled builds an object map of ignored methods. It then calls `$.ajaxSetup({ beforeSend: addRestCsrfCustomHeader })`.

For every later jQuery AJAX request, the callback returns immediately unless `settings.url` starts with `/webhdfs/`. It then reads `settings.type` and skips the request if the method is in the ignore map. For protected methods, it adds the configured header with a placeholder value because WebHDFS only requires header presence.

## State and Persistence Behavior
The script stores CSRF configuration only in closure variables and jQuery's global AJAX setup for the current page. It does not persist configuration in cookies, local storage, or server state. Configuration changes on the server require a page reload to be reflected in client behavior.

`$.ajaxSetup` is page-global. Later code that overwrites `beforeSend` through another `ajaxSetup` call could disable this protection unless it explicitly chains the previous callback.

## Dependencies and Integration Points
This file depends on jQuery and browser support for `String.prototype.startsWith`. It also depends on the NameNode `/conf` endpoint returning XML with the WebHDFS CSRF properties when configured.

The main integration point is `hdfs/explorer.html`, which loads this script before `explorer.js`. The explorer issues WebHDFS operations such as `GET_BLOCK_LOCATIONS`, `OPEN`, `LISTSTATUS`, `SETOWNER`, `SETREPLICATION`, and deletes/mutations through `/webhdfs/v1...`; this script ensures mutating or otherwise protected requests carry the required CSRF header when server-side enforcement is enabled.

The relevant server-side/documentation integration is the WebHDFS configuration documented in `src/site/markdown/WebHDFS.md`, including enabled flag, custom header name, ignored methods, and browser user-agent matching.

## Risks and Edge Cases
- The initial `/conf` request is synchronous and blocks page loading. This enforces ordering but can degrade UX or fail under browser policies that discourage sync XHR on the main thread.
- If `/conf` fails, the `.done` callback never runs and no CSRF hook is installed. A CSRF-enabled server would then reject protected WebHDFS requests rather than showing a specific configuration error.
- Method matching is case-sensitive because ignored methods are stored exactly as configured and compared to `settings.type`. jQuery defaults are usually uppercase, but inconsistent case in config or request options could cause unexpected header injection or omission.
- Only URLs starting with `/webhdfs/` are covered. Absolute URLs, alternate prefixes, or redirected DataNode URLs are intentionally outside this hook.
- The script replaces the global `beforeSend` option. Other global AJAX setup code can conflict unless composed carefully.
- `startsWith` may not exist in very old browsers; this is acceptable for modern Hadoop web UI assumptions but is still a compatibility point.

## Test Signals
No direct unit test was in the researched set. Browser/integration tests should enable WebHDFS CSRF protection, load the explorer, and verify that protected `/webhdfs/` methods include the configured header while ignored methods do not. Tests should also cover a failed `/conf` load, lowercase method values, and interaction with any other global jQuery AJAX setup.
