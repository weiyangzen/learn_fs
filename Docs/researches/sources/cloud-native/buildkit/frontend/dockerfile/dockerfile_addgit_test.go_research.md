# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_addgit_test.go

Purpose: integration-tests Dockerfile ADD and build context Git URL behavior, including SHA-1/SHA-256 repos, query-string syntax, checksums, subdirs, submodules, keep-git-dir, and cache behavior.

Important tests: `testAddGitSHA1`, `testAddGitSHA256`, shared `testAddGit`, `testAddGitChecksumCache`, and `testGitQueryString`. Helper `applyTemplate` renders Dockerfile templates.

Control flow: tests create local Git repositories, commits/tags/branches/submodules, serve them over HTTP, then run frontend solves with local mounts or Git context URLs. Cases verify file contents, git metadata presence/absence, chown behavior, checksum success/mismatch/invalid errors, cache reuse when checksum is added, query `ref`/`branch`/`tag`/`commit`/`subdir`/`keep-git-dir`/`submodules` behavior for both build context and ADD.

State and persistence: uses temp Git repos, HTTP servers, BuildKit cache, and local exporter output dirs. Windows skips reflect Git source handler limitations.

Dependencies and integration: exercises `dfgitutil`, `convert_copy.go`, Git source resolver, local exporter, frontend attrs, and BuildKit client.

Risks and test signals: very high-value regression coverage for Git semantics and cache keys. Risks include dependency on local git command, HTTP dumb Git serving, platform skips, and exact error text.
