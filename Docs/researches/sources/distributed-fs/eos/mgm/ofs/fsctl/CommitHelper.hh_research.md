## sources/distributed-fs/eos/mgm/ofs/fsctl/CommitHelper.hh

Purpose: declaration for the `CommitHelper` utility class used by the fsctl commit path.

Important APIs and types: `CommitHelper`, thread-local `eos::common::LogId tlLogId`, typedefs `cgi_t`, `option_t`, `param_t`, `path_t`, and static helper methods for checksum conversion, filesystem checks, CGI parsing, option setup, OC initialization, reconstruction detection, parameter checks, scheduler removal, size/checksum validation, location/checksum/OC handling, metadata commit, version fid lookup, versioning handling, and timestamp collision adjustment.

Control flow role: the header defines the functional decomposition used by `Commit.cc`. Public static methods split commit handling into parse, validate, mutate metadata, and version/atomic phases. `IncrementTsForVersionFn()` is private in production but exposed under `IN_TEST_HARNESS`, indicating it has or should have unit coverage.

State and persistence behavior: no implementation here, but the API surface shows helper methods mutate global MGM state through `gOFS`, file metadata, quota, scheduler/tracker state, and path maps. The `option_t` map is a mutable control-plane object shared between helper calls and the main commit function.

Dependencies and integration points: includes logging, path, mapping, namespace, and `IFileMD` interfaces. The header is included by `Commit.cc` and `CommitHelper.cc`.

Risks: option and parameter maps use string keys rather than typed structs, so missing or misspelled keys silently default through `operator[]` in the implementation. `path_t` stores `eos::common::Path` objects and relies on specific keys such as `atomic`, `version`, and `versiondir`.

Test signals: compile-time interface consistency with `Commit.cc`, test-harness access to `IncrementTsForVersionFn`, typed expectations around all string-map keys, and ABI/namespace macro correctness.
