<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/registry/search.go -->
# sources/cloud-native/moby/api/types/registry/search.go

## Purpose
SearchResult describes a search result returned from a registry

## Important APIs, Types, And Functions
- Exported types: SearchResult, SearchResults.
- `SearchResult` fields include StarCount, IsOfficial, Name, IsAutomated, Description.
- `SearchResults` fields include Query, NumResults, Results.
- Wire JSON fields include description, is_automated, is_official, name, num_results, query, results, star_count.
- Source comments highlight: SearchResult describes a search result returned from a registry SearchResults lists a collection search results returned from a registry

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- The file contains deprecated fields or comments; compatibility requires retaining them even when newer fields exist.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/registry/search.go -->
