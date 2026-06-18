# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestTableMapping.java

## Purpose
Tests file-backed `TableMapping` host-to-rack resolution, caching, missing/bad file fallback, cache clearing, and reload behavior.

## Important APIs, Types, And Functions
Uses `TableMapping`, config key `NET_TOPOLOGY_TABLE_MAPPING_FILE_KEY`, `resolve()`, `reloadCachedMappings()`, Guava `Files.asCharSink()`, and temp files.

## Control Flow
Tests create temporary mapping files with space/tab-separated host and rack entries, configure mapping, and resolve two host names. Caching test modifies config after first read and expects cached results. No-file, missing-file, and bad-file tests expect default rack. Clearing test empties the map file, reloads, and expects default rack.

## State And Persistence Behavior
State exists in temp files and the mapping's internal cache. Files are marked `deleteOnExit`. Reload clears/reloads cached mappings from file content.

## Dependencies And Integration Points
Validates topology table mapping for deployments that use a static host/rack file instead of scripts.

## Risks
Bad file parsing should not throw to callers but should fall back to default rack. Cache can hide later config/file changes until reload. Temp-file cleanup relies on JVM exit.

## Test Signals
Expected signals are `/rack1` and `/rack2` for valid files, same cached values after config points to a bad path, and `/default-rack` for missing, nonexistent, emptied, or malformed files.
