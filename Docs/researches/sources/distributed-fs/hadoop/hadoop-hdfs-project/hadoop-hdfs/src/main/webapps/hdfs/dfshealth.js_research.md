# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/hdfs/dfshealth.js

## Purpose

`dfshealth.js` drives the NameNode web UI health pages. It compiles Dust templates, loads NameNode JMX and configuration endpoints, normalizes server-provided JSON strings, renders overview/startup/DataNode/snapshot tabs, and wires hash-based navigation for the HDFS health dashboard.

## Important APIs and functions

- `load_overview()` fetches NameNode, FSNamesystem, replicated block, erasure-coded block, storage-type, and JVM memory beans through `/jmx`, plus HA identity from `/conf`.
- `guard_with_startup_progress(fn)` catches `TypeError` from incomplete JMX responses and redirects to `load_startup_progress()`.
- `load_startup_progress()` renders `/startupProgress` data and renames nested keys that conflict with Dust lookup behavior.
- `load_datanode_info()` parses node maps, derives DataNode state/link fields, initializes DataTables, and renders a D3 disk-usage histogram.
- `load_datanode_volume_failures()` filters live DataNodes to only nodes with volume failures.
- `load_snapshot_info()`, `getSubTableId()`, and `formatExpandedRow()` render snapshottable directories and expandable per-snapshot tables.
- `$.fn.dataTable.ext.order['ng-value']` sorts columns by rendered `ng-value` attributes.

## Control flow

On load, the script compiles five templates, calls `load_page()`, and re-runs page loading on `hashchange`. `load_page()` switches on `window.location.hash`, defaulting to `#tab-overview`. The overview path starts an asynchronous `/conf` request and a multi-bean `load_json` request; rendering waits until either non-HA mode is known or HA namespace/NameNode ID has been populated.

DataNode tabs fetch `NameNodeInfo`, convert JMX string maps into arrays, derive display state, render the tab template, and then initialize DataTables and D3 after the DOM is inserted. Snapshot loading fetches `SnapshotInfo`, renders the table, builds a `snapshotDirectory` grouping map, and lazily initializes nested DataTables when a details row is expanded.

## State and persistence behavior

State is browser-local and transient. The script stores tab content in the DOM, current tab selection in the URL hash, and live DataNode data on `window.liveNodes` for histogram click integration with external page code. No data is persisted to storage. The overview has a short polling loop waiting for `/conf`; DataTables and D3 mutate DOM state after each render.

## Dependencies and integration points

The file depends on jQuery, Dust, Moment, DataTables, D3, Bootstrap tabs, Hadoop's shared `load_json`, `/jmx`, `/conf`, and `/startupProgress` endpoints, and HTML templates embedded in the NameNode page. It integrates with JMX bean shapes that expose several fields as JSON-encoded strings rather than structured JSON.

## Risks and edge cases

- Several JMX attributes are parsed with `JSON.parse`; malformed or schema-changed strings break rendering.
- `guard_with_startup_progress` catches only `TypeError`, which may hide unrelated template or schema bugs as startup-progress redirects.
- Overview rendering depends on a 5 ms polling interval around `/conf`; a failed `/conf` request leaves the page waiting unless `non_ha` is set.
- Helper-generated HTML in `helper_dir_status` is built by string concatenation and assumes trusted JMX/config values.
- Histogram width is computed once from `div.container`; resize behavior is not handled.
- Snapshot root extraction assumes `.snapshot` is present in the directory string.

## Test signals

Useful coverage would stub `/jmx`, `/conf`, and `/startupProgress` responses for HA and non-HA clusters, malformed JMX string fields, NameNode startup responses, IPv4/IPv6 DataNode addresses, secure DataNode addresses, maintenance/decommission states, volume-failure filtering, DataTables sorting by `ng-value`, and snapshot expansion. UI tests should verify tab hash routing and that error panels appear for failed endpoint requests.
