## sources/cloud-native/moby/daemon/internal/lazyregexp/lazyregexp.go

Purpose: Provides a lazy wrapper around `regexp.Regexp` for global regex variables without init-time compilation cost.

Important APIs/types: `Regexp` stores the pattern string, `sync.Once`, and compiled regexp pointer. `New` constructs a lazy regexp and eagerly compiles in test binaries. Wrapper methods expose common regexp operations: submatches, all string submatches, string match/index, replace, find, match, replace func, and subexpression names.

Control flow: First method call invokes `re`, which runs `build` once. `build` calls `regexp.MustCompile`, stores the compiled regexp, and clears the original string. `inTest` detects test binaries by executable name ending `.test` (after trimming `.exe`) so invalid regexps panic during tests rather than later at runtime.

State and persistence: In-memory cached compiled regex only. No persistence.

Dependencies and integration: Based on Go module lazyregexp pattern, used by packages with package-level regexps.

Risks: Invalid patterns panic on first use in production. After compilation, the original pattern string is cleared, so debugging relies on `regexp.Regexp` string output. Only wrapped regexp methods are available.

Test signals: `lazyregexp_test.go` confirms eager test panic for invalid regex and basic valid matching.
