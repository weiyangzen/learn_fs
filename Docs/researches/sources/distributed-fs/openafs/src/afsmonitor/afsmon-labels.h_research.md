# sources/distributed-fs/openafs/src/afsmonitor/afsmon-labels.h

## Purpose

`afsmon-labels.h` defines the variable names, display labels, and section/group category ranges that let `afsmonitor` map positional xstat data to readable UI/output columns.

## Important Data

`fs_varNames[]`, `fs_labels[]`, and `fs_categories[]` describe file server stats: performance counters, vnode cache, directory package, Rx, host module, busies, RPC timings, transfer timings, and callback counters. `cm_varNames[]`, `cm_labels[]`, and `cm_categories[]` describe cache manager stats: cache use, server up/down records, FS/VL RPC timings and errors, transfer timing, CM callback RPC timing, authentication/PAG state, and replicated access counters.

## Control Flow

The header has no functions. Its strings encode a positional contract: labels and categories are looked up by array index, and category strings contain hard-coded inclusive index ranges.

## State and Persistence Behavior

The arrays become static program data. They do not persist runtime state, but they define the long-lived interpretation of monitor columns and logs.

## Dependencies and Integration Points

The file includes `afsmonitor.h` and must stay aligned with `xstat_fs.h`, `xstat_cm.h`, `afsmon-output.c`, parser expectations, and UI category parsing.

## Risks and Test Signals

Parallel arrays and hard-coded ranges can drift when xstat structures change. Header-level definitions can cause duplicate definitions if included from multiple translation units. Test array counts, label/name count equality, range bounds, category parsing, and UI rendering of long labels.
