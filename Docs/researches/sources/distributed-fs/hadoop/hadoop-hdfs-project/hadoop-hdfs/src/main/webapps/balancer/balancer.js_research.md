<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/balancer/balancer.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/balancer/balancer.js

## Purpose
This browser-side script powers the HDFS Balancer web UI overview tab. It fetches Balancer-related JMX beans, normalizes a few fields for the Dust template, derives host/start-time display fields, and renders the `#tmpl-balancer` template into `#tab-overview`.

## Important APIs, Types, And Functions
- The module is an immediately invoked function expression using strict mode and a private `data` object.
- `dust.loadSource(dust.compile($('#tmpl-balancer').html(), 'balancer'))` compiles the page template.
- `BEANS` declares three JMX requests: MBean server info, singleton `Hadoop:service=Balancer,name=BalancerInfo`, and wildcard `Hadoop:service=Balancer,name=Balancer-*`.
- External helper `load_json(BEANS, success, failure)` performs the grouped asynchronous data load.
- `guard_with_startup_progress(fn)` wraps success processing and shows a startup-progress-friendly message for `TypeError`.
- `workaround(balancers)` derives `BlockPoolID` from each balancer bean's `modelerType` suffix after `-`.
- `extractMetrics()` parses `MBeanServerId` into `HostName` and `BalancerStartedTimeInMillis`.
- `HELPERS.helper_date_tostring` formats millisecond timestamps using Moment.js.
- `render()` creates a Dust base with helpers and injects rendered HTML into `#tab-overview`.
- `show_err_msg()` displays the alert panel with a generic Balancer load failure.

## Control Flow
On page load the script compiles the template, declares required JMX beans, and invokes `load_json`. The success callback copies each response into `data`: wildcard balancer beans are passed through `workaround`, while singleton beans use the first returned bean. It then calls `extractMetrics()` and `render()`. The failure callback invokes `show_err_msg`; the success callback is additionally wrapped to catch `TypeError`, which commonly happens when the Balancer HTTP server starts before all expected JMX beans are available.

## State And Persistence
All state is in the page-local `data` object and the DOM. The script persists nothing to browser storage or the server. It mutates bean objects in memory by adding `BlockPoolID`, `HostName`, and `BalancerStartedTimeInMillis` before rendering.

## Dependencies And Integration Points
The script depends on jQuery (`$`), Dust.js, `dust.helpers.tap`, Moment.js, Hadoop's shared `load_json` helper, a DOM template with id `tmpl-balancer`, an overview tab with id `tab-overview`, and alert elements `alert-panel` / `alert-panel-body`. Its backend integration is the Balancer HTTP server's `/jmx` endpoint and the Hadoop JMX object names listed in `BEANS`.

## Risks And Edge Cases
- `workaround` assumes every wildcard bean has a `modelerType` containing `-`; if not, `BlockPoolID` becomes an unexpected substring.
- `extractMetrics` assumes `MBeanServerId` is `host_timestamp`; missing `_` falls back to `"invalid data"`.
- The guard catches only `TypeError`, so template errors or other runtime exceptions may fail silently through the Dust callback path or surface in the browser console.
- `dust.render` ignores its `err` argument and writes `out` unconditionally, which can hide template failures.
- Error display discards the detailed URL/cause passed by the failure callback, reducing diagnosability.
- The UI trusts JMX response shape. Missing `beans[0]` during startup or with incompatible Hadoop versions is the main fragility.

## Test Signals
Useful tests include loading the Balancer UI against a running balancer HTTP server, mocking `/jmx` responses for all three bean queries, checking `BlockPoolID` derivation for multiple block pools, testing startup responses with missing beans, verifying Moment formatting of start time, and browser/JS tests that assert `#tab-overview` receives rendered content or `#alert-panel` appears on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/balancer/balancer.js -->
