# sources/distributed-fs/eos/mgm/proc/user/Who.cc

Purpose: implements `ProcCommand::Who()`, reporting active client sessions grouped by user, authentication protocol, and optionally individual clients.

Important APIs and types: reads `mgm.option` and `mgm.format`, uses `Mapping::ActiveTidentsSharded`, `StringConversion::Tokenize`, `Mapping::UidToUserName`, JsonCpp `Json::Value` and stream writer, and writes to `stdOut` or `stdJson`.

Control flow: parses flags for monitoring, clients, auth summary, all, summary-only, and numeric IDs. It snapshots active tident shards into an unordered map, counts users and auth protocols, then emits selected auth counts, user counts, client records, and total client summary in monitoring, JSON, or human-readable format.

State and persistence: read-only except stats. It copies active session entries before detailed output, reducing time spent reading sharded state.

Dependencies and integration: consumes global active identity/session tracking and name mapping services.

Risks: tident parsing assumes caret-delimited tokens with at least uid, client, auth, and gateway fields; malformed entries can index missing tokens. JSON output is an array of heterogeneous objects, not a structured object with named sections. Tests should cover numeric and translated IDs, monitoring and JSON formats, malformed/short tident strings, showclients/showall/showsummary combinations, auth summaries, and idle time calculation.
