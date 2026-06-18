<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_server_prefs.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/cm_server_prefs.c

## Purpose
Demonstrates listing cache-manager server preference ranks over the CM stats interface.

## Important APIs, Types, And Functions
The file defines `Usage`, `ParseArgs`, and `main`, and uses `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_CMStatOpenPort`, `util_CMGetServerPrefsBegin/Next/Done`, `afsclient_CMStatClose`, and `afsclient_CellClose`. Each row is an `afs_CMServerPref_t` with `ipAddr` and `ipRank`.

## Control Flow
After connecting to the selected host and port, `main` starts the preference iterator, prints an address/rank header, loops through every preference, checks for `ADMITERATORDONE`, closes the iterator and resources, and exits.

## State And Persistence
It reads a transient snapshot of cache-manager ranking state and writes only stdout/stderr. Iterator ownership belongs to the util layer.

## Dependencies And Integration Points
It uses libadmin CM stat connections and the utility admin server-preference iterator. It integrates with the same sample build infrastructure as the other CM samples.

## Risks And Test Signals
Manual IP formatting and fail-fast cleanup are the main risks. Tests should compare output against a cache manager with known server preferences, including multiple ranks and an empty preference table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_server_prefs.c -->
