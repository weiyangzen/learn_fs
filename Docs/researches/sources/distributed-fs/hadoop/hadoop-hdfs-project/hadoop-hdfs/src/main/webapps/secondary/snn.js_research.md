# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/secondary/snn.js

## Purpose

`snn.js` renders the SecondaryNameNode web UI overview. It combines the SecondaryNameNode JMX bean with checkpoint-related configuration values from `/conf`, then renders the `snn` Dust template.

## Important APIs and functions

- `load()` starts two asynchronous requests: `/jmx?qry=Hadoop:service=SecondaryNameNode,name=SecondaryNameNodeInfo` and `/conf`.
- `finished_request()` counts both request completions, enriches `data.snn` with `CheckpointPeriod` and `TxnCount`, and renders only when both requests succeeded.
- `render()` writes the `snn` template into `#tab-overview` and marks it active.
- `show_error_msg(msg)` displays load failures in the alert panel.

## Control flow

On load, the script compiles `#tmpl-snn`, initializes `outstanding_requests` to 2, and calls `load()`. Each request's `always` handler decrements the counter. Once both complete, success requires both `data.snn` and `data.conf`; otherwise the page shows a generic failure. The configuration XML is flattened into a name-to-value object before render.

## State and persistence behavior

State is in-memory only: `data` holds the JMX bean and config map, and `outstanding_requests` coordinates the two async completions. There is no polling, URL state, browser storage, or persistence.

## Dependencies and integration points

The file depends on jQuery, Dust, Bootstrap-compatible tab markup, `/jmx`, and `/conf`. It assumes `/conf` exposes `dfs.namenode.checkpoint.period` and `dfs.namenode.checkpoint.txns`, and that `SecondaryNameNodeInfo` is present as the first JMX bean.

## Risks and edge cases

- Failures do not preserve endpoint-specific error detail.
- Missing config properties still render as undefined fields rather than a targeted warning.
- Additional or zero JMX beans are not validated.
- The request counter is fixed at 2, so future request additions must update it carefully.

## Test signals

Tests should cover both successful request orderings, one or both request failures, missing config keys, malformed `/conf` XML, empty JMX beans, and template output containing checkpoint period and transaction-count values.
