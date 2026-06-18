<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/datanode/dn.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/datanode/dn.js

## Purpose
This browser-side script powers the HDFS DataNode web UI overview tab. It retrieves the DataNode JMX info bean, converts JSON-encoded fields into structures suitable for templating, derives the displayed host name, and renders the `#tmpl-dn` Dust template.

## Important APIs, Types, And Functions
- The module is an immediately invoked function expression using strict mode and a private `data` object.
- `dust.loadSource(dust.compile($('#tmpl-dn').html(), 'dn'))` compiles the DataNode template.
- `load()` issues `$.get('/jmx?qry=Hadoop:service=DataNode,name=DataNodeInfo', success).fail(show_err_msg)`.
- `workaround(dn)` normalizes JMX bean fields before rendering.
- `node_map_to_array(nodes)` converts an object map into an array and injects each map key as `p.name`.
- `render()` defines `helper_relative_time`, renders template `dn`, and activates `#tab-overview`.
- `show_err_msg()` displays a generic DataNode load failure in the alert panel.

## Control Flow
After initialization, `load()` runs immediately. The JMX success callback takes `resp.beans[0]`, passes it to `workaround`, copies `DatanodeHostname` to `data.dn.HostName`, and calls `render()`. `workaround` parses `dn.VolumeInfo` from a JSON string to an object map, converts that map to an array for template iteration, and parses `dn.BPServiceActorInfo` from a JSON string. `render()` builds a Dust base with a relative-time helper backed by Moment.js, renders `dn`, writes output into `#tab-overview`, and marks the tab active.

## State And Persistence
State is held only in the page-local `data` object and DOM. The script does not persist to local storage or the server. It mutates the JMX bean object by replacing `VolumeInfo` and `BPServiceActorInfo` strings with parsed data and by adding `HostName`.

## Dependencies And Integration Points
The script depends on jQuery, Dust.js, `dust.helpers.tap`, Moment.js, the DOM template `#tmpl-dn`, the overview and alert DOM nodes, and the DataNode HTTP server's `/jmx` endpoint. It is tightly coupled to the JMX schema for `Hadoop:service=DataNode,name=DataNodeInfo`, especially `VolumeInfo`, `BPServiceActorInfo`, and `DatanodeHostname`.

## Risks And Edge Cases
- Missing `resp.beans[0]`, malformed JSON in `VolumeInfo` or `BPServiceActorInfo`, or schema changes throw before render and are not caught by the `.fail()` network handler.
- `node_map_to_array` mutates each volume object by assigning `name`; if a parsed volume entry is not an object, this can fail or produce surprising data.
- `render()` ignores the Dust `err` argument and writes `out` unconditionally.
- `helper_relative_time` assumes the supplied value is seconds and numeric; bad values produce confusing relative-time text.
- The error message is generic and does not expose HTTP status or parse failure details.

## Test Signals
Useful signals include loading the DataNode UI against a live MiniDFSCluster/DataNode, mocking the JMX endpoint with valid and invalid `VolumeInfo`/`BPServiceActorInfo`, verifying volume map-to-array conversion and `HostName` derivation, checking the relative-time helper with known values, and browser tests that assert overview rendering or alert display on request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/datanode/dn.js -->
