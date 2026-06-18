# sources/cloud-native/containers-storage/pkg/regexp/regexp_test.go

Purpose: tests the delayed regexp wrapper.

Important APIs, types, and functions: interface `partOfRegexp`, compile-time assignment `var _ partOfRegexp = &Regexp{}`, `TestMatchString`, and `TestFindStringSubmatch`.

Control flow: tests create delayed regexes, call matching/submatch methods, and assert expected match and non-match outcomes.

State and persistence: no persistence. Tests cause lazy compilation under default builds.

Dependencies and integration points: depends on `testing`. It validates enough wrapper surface to catch broken embedding/delegation for common methods.

Risks and edge cases: only a tiny subset of the delegated methods is tested. Invalid pattern panic behavior and precompile build tag behavior are not explicitly tested.

Test signals: confirms lazy wrapper implements expected methods and delegates match/submatch operations correctly.
