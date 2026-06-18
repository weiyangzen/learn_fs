# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dfs-dust.js

## Purpose
Hadoop-specific Dust.js extension layer for HDFS web pages. It adds formatting filters used by inline Dust templates and exposes a shared `load_json` helper for fetching multiple JMX endpoints before rendering.

## Important APIs, Types, And Functions
The IIFE receives `jQuery`, `dust`, and `window`. It defines filters and merges them into `dust.filters` with `$.extend`. Filters are `fmt_bytes`, `fmt_percentage`, `fmt_time`, `date_tostring`, `format_compile_info`, `helper_to_permission`, `helper_to_directory`, `helper_to_acl_bit`, `fmt_number`, and `fmt_human_number`. The exported API is `window.load_json(beans, success_cb, error_cb)`, where `beans` entries are objects with `url` and `name`.

## Control Flow
Filter functions are invoked by Dust templates during render, for example `{Total|fmt_bytes}` or `{PercentUsed|fmt_percentage}`. `load_json` starts one `$.get` per bean. Each successful response is stored as `data[b.name]`; a countdown is decremented; when all outstanding requests complete, `success_cb(data)` runs. On the first failed request, an `error` flag is set and `error_cb(url, jqxhr, text, err)` runs. The `$.each` callback stops launching later requests if the error flag is already set, though requests already started can still finish.

## State And Persistence
No persistent storage is used. Filter registration mutates the global `dust.filters` object for the current page. `load_json` maintains per-call in-memory `data`, `error`, and `to_be_completed` variables. Numeric and date formatting is stateless apart from relying on the global `moment` object for date conversion.

## Dependencies And Integration Points
Depends on jQuery, Dust core, and Moment.js. It must be loaded after `dust-full-2.0.0.min.js`, `dust-helpers-1.1.1.min.js`, and `moment.min.js` where date filters are used. It is included by NameNode, DataNode, JournalNode, SecondaryNameNode, Balancer, and Explorer pages. `hdfs/dfshealth.js` and `journal/jn.js` use `load_json` for JMX fan-out; many templates in `dfshealth.html`, `explorer.html`, `datanode.html`, and `balancer.html` consume the filters.

## Risks
The comment says "Load a sequence of JSON", but the implementation launches asynchronous requests concurrently. `load_json([])` never calls `success_cb` because the countdown starts at zero and no request decrements it. `fmt_number` calls `v.toLocaleString()` and will fail for `null`/`undefined`. `format_compile_info` assumes the input contains `" by "` and will append `undefined` if it does not. `fmt_bytes` and `fmt_human_number` do not explicitly handle negative, `NaN`, or infinite inputs. `helper_to_permission` mixes parsed octal state with decimal digit extraction from the original value, so malformed permission strings can produce misleading output.

## Test Signals
Unit-style browser tests can call each filter with boundary values: `0`, `1`, powers of `1024`, large byte values, `-1`, missing compile-info delimiters, sticky permissions such as `1755`, and directory/ACL booleans. For `load_json`, stub `$.get` to verify all named responses are collected, first failure calls the error callback with the failing URL, already-started successes after failure do not trigger success, and the empty-bean behavior is either documented or fixed.
