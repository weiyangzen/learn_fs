# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/journal/jn.js

## Purpose

`jn.js` renders the JournalNode overview page. It loads JournalNode JMX beans, derives display-friendly journal nameservice fields, and renders the `jn` Dust template into the overview tab.

## Important APIs and functions

- `BEANS` describes two JMX queries: `JournalNodeInfo` and all `Journal-*` MBeans.
- `workaround(journals)` extracts `NameService` from each journal bean's `modelerType` suffix after the first `-`.
- `guard_with_startup_progress(fn)` catches `TypeError` and reports a JournalNode-specific load error.
- `render()` renders the `jn` Dust template with a helper that formats epoch milliseconds using Moment.
- `show_err_msg()` displays a fixed alert message.

## Control flow

The script compiles `#tmpl-jn`, invokes shared `load_json` with both bean descriptors, stores `journals` as the transformed array and `jn` as the first info bean, then renders the overview tab and marks it active. Any endpoint failure or guarded `TypeError` shows the alert panel.

## State and persistence behavior

State is limited to an in-memory `data` object and rendered DOM. There is no URL, storage, or polling state. Rendering is single-shot at page load.

## Dependencies and integration points

The file depends on jQuery, Dust, Moment, Bootstrap tab markup/classes, shared Hadoop `load_json`, and `/jmx` JournalNode MBeans. It assumes the `modelerType` naming convention contains a hyphen-delimited nameservice suffix.

## Risks and edge cases

- `show_err_msg` ignores the passed error message, so detailed endpoint failures are lost.
- `workaround` uses the first hyphen in `modelerType`; unexpected naming can produce the full string or an incorrect suffix.
- Empty `beans` arrays lead to undefined template data and may be reported only as a generic failure.
- There is no retry or startup-progress page, only an alert.

## Test signals

Tests should provide successful multi-bean JMX fixtures, empty/malformed bean fixtures, modeler types with and without hyphens, endpoint failure callbacks, and template-render assertions for formatted dates and active tab state.
