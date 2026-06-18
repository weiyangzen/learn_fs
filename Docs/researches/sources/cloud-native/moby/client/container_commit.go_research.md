<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_commit.go -->
# sources/cloud-native/moby/client/container_commit.go

Purpose: creates a new image from a container’s filesystem changes.

Important APIs/types/functions: `ContainerCommitOptions`, `ContainerCommitResult{ID}`, and `Client.ContainerCommit`.

Control flow: validates container id, parses an optional normalized reference, rejects digest references, extracts repository/tag, builds query fields (`container`, `repo`, `tag`, `comment`, `author`, repeated `changes`, optional `pause=0`), posts optional container config to `/commit`, closes the response, and decodes `container.CommitResponse.ID`.

State and integration behavior: no local persistence; daemon creates image state. Depends on distribution reference parsing, shared request helpers, JSON decoding, and container API types.

Risks and test signals: risks are reference normalization, accidentally accepting digest tags, query encoding of Dockerfile changes, and pause semantics. `container_commit_test.go` asserts errors, invalid ids, route, query fields, `NoPause`, and response ID decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_commit.go -->
