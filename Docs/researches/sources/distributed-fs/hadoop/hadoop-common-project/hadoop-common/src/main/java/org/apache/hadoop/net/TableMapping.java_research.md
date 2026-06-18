# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/TableMapping.java

Purpose: DNS-to-rack mapping implementation backed by a two-column UTF-8 text file configured via `net.topology.table.file.name`.

Important APIs/types/functions: constructor, `getConf`, `setConf`, `reloadCachedMappings`, nested `RawTableMapping.load`, `resolve`, and reload overloads.

Control flow: `resolve` lazily loads the file into a map, falling back to an empty map and default rack on load failure. `load` trims lines, skips blanks and comments, accepts exactly two whitespace-separated columns, and logs ignored malformed lines. Reload attempts a fresh full-table load and only swaps the map on success.

State and persistence: in-memory `map` cache in `RawTableMapping`; source of truth is the external table file. Outer class adds `CachedDNSToSwitchMapping` caching.

Dependencies and integration: depends on Hadoop `Configuration`, `Configured`, `NET_TOPOLOGY_TABLE_MAPPING_FILE_KEY`, and topology default rack. Used as an alternative to script-based mapping.

Risks: malformed or unreadable files silently degrade to default rack on initial load. Reload failure preserves stale mappings. Per-name reload reloads the whole file. Lookups are exact; host normalization is not done here.

Test signals: `TestTableMapping` covers parsing, fallback, reload, comments, and malformed lines.
