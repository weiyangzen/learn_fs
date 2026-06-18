# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/histogram-hostip.js

## Purpose
Small HDFS-specific browser helper for the DataNode usage histogram. It lets users click a D3 histogram bar and see the DataNode host/IP addresses whose disk usage falls inside that bin.

## Important APIs, Types, And Functions
The file defines two global functions: `open_hostip_list(x0, x1)` and `close_hostip_list()`. `open_hostip_list` reads the global `liveNodes` array, filters DataNodes by `(dn.usedSpace / dn.capacity) * 100.0`, extracts host/IP text from `dn.infoAddr`, creates a read-only `<textarea id="datanode_ips">`, creates a clickable `<div id="close_ips">X</div>`, and appends both under `#datanode-usage-histogram`. `close_hostip_list` removes those two elements with jQuery selectors.

## Control Flow
`hdfs/dfshealth.js` sets `window.liveNodes = dnData.LiveNodes` in `renderHistogram`. It attaches an inline `onclick` attribute to each D3 bar rectangle that calls `open_hostip_list(d.x0, d.x1)`. When invoked, `open_hostip_list` first removes any existing list, scans all live nodes, coerces zero usage to `1` so empty nodes are included in the first positive bin, excludes nodes above the clicked range, and writes one address per line into the textarea. Clicking the `X` div calls `close_hostip_list`.

## State And Persistence
The helper relies on page-global mutable state: `window.liveNodes` supplied by `dfshealth.js`. Its own state is DOM state: a relative-position style on `#datanode-usage-histogram`, the generated textarea, and the generated close div. Nothing is persisted across page loads.

## Dependencies And Integration Points
Depends on jQuery for removal and on the DOM element `#datanode-usage-histogram` from `dfshealth.html`. It is loaded by `dfshealth.html` after `dfshealth.js`; that order is acceptable because the functions only need to exist when a user later clicks a histogram bar. It is tightly coupled to DataNode objects containing `usedSpace`, `capacity`, and `infoAddr`, and to the bin bounds produced by D3's `histogram()`.

## Risks
The script assumes `liveNodes` exists and is an array; clicking before histogram setup or after a failed JMX request would throw. Division by zero or missing capacity can produce invalid usage values. The IPv6 parser only handles bracketed `host]:port` patterns and strips the leading `[`, while IPv4/hostname parsing splits at the first colon. The close div style contains `height;20px`, a typo that leaves height unset. Setting inline `onclick` and writing `innerHTML` are acceptable with current generated values, but using `textContent`/event listeners would be safer and easier to audit.

## Test Signals
Create a page fixture with `#datanode-usage-histogram` and a `liveNodes` array containing IPv4, hostname, and bracketed IPv6 `infoAddr` values. Call `open_hostip_list(0, 5)` and verify the textarea contains the expected one-address-per-line list, previous generated nodes are removed on repeated calls, and `close_hostip_list()` removes both generated elements. Include boundary checks for exactly `x0`, exactly `x1`, zero usage, and usage above 100 percent.
