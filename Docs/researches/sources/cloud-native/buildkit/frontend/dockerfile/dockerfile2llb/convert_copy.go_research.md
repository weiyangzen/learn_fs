# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_copy.go

Purpose: implements ADD and COPY dispatch into LLB file operations, including local context copies, stage copies, remote HTTP ADD, Git ADD, heredoc source contents, checksums, chmod/chown, exclude patterns, parents mode, link mode, and unpack behavior.

Important APIs: `copyConfig` carries instruction-specific settings; `dispatchCopy` performs conversion; `isHTTPSource`, `isGitSource`, and `containsWildcards` classify sources.

Control flow: destination is normalized relative to workdir. Copy options are assembled for chown, chmod, and exclude patterns. Chmod accepts octal up to `07777` or symbolic modes via `dchapes-mode`. Checksums are restricted to ADD with exactly one HTTP(S) or Git source. Each source is handled as Git, HTTP, local path, or inline content. Git sources map query/flags to `llb.GitOption`; HTTP sources use `llb.HTTP` with optional digest and no default unpack; local copies normalize source paths, validate `.dockerignore` warnings, and configure wildcard/required path behavior. Link mode can use merge op when caps permit.

State and persistence: mutates `dispatchState.state` and image history. Context path usage is recorded by caller in `convert.go`.

Dependencies and integration: uses `dfgitutil`, Dockerfile instructions, LLB copy/http/git, system path helpers, pattern matcher, identity progress groups, and solver caps.

Risks and test signals: risks include checksum/ref conflict handling, COPY accidentally accepting remote refs, Windows path normalization, symbolic chmod compatibility, link-mode command indexing, and wildcard required paths. Covered by ADD checksum/Git/chmod integration tests and exclude pattern tests.
