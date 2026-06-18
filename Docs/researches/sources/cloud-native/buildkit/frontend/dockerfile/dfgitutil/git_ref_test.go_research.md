# sources/cloud-native/buildkit/frontend/dockerfile/dfgitutil/git_ref_test.go

Purpose: validates Dockerfile Git URL parsing and fragment formatting.

Important test cases: HTTP(S) `.git` enforcement, legacy `github.com/` ambiguity, SSH-style refs, fragment ref/subdir parsing, query `ref`, `tag`, `branch`, `subdir`, `checksum`/`commit`, `keep-git-dir`, `submodules`, `mtime`, and `fetch-by-commit`, plus conflict and invalid parameter errors.

Control flow and state: table-driven tests call `ParseGitRef` and compare full `GitRef` structs or expected error substrings. Separate tests call `FragmentFormat` with and without subdir.

Dependencies and integration: guards behavior consumed by Dockerfile ADD Git and Git build context integration tests.

Risks and test signals: strong regression coverage for parser rules; does not execute remote Git resolution, which is covered by `dockerfile_addgit_test.go`.
