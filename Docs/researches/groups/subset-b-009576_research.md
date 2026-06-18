# Research Group: subset-b-009576

This grouped report covers gcsfuse root command parsing fixtures, common helpers, auth helpers, block memory/pool primitives, buffered read prefetching, and the CSI driver Cloud Build pipeline. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/root_test.go -->
# Research: sources/user-network-fs/gcsfuse/cmd/root_test.go

Purpose: comprehensive unit coverage for the Cobra/Viper root command path. It verifies argument arity, POSIX-style flag normalization, bucket/mount-point extraction, config-file unmarshalling, validation, optimization/rationalization precedence, and logging metadata capture before the real mount function is called.

Important APIs/types/functions: `createTempConfigFile`, `newRootCmd`, `convertToPosixArgs`, `getCliFlags`, `getConfigFileFlags`, and the injected `mountFn` callback are the tested surfaces. The cases cover `cfg.Config` subtrees for write/read/file-cache/auth/connection/filesystem/list/metrics/trace/metadata-cache/retries/profiler/dummy-io/workload-insight plus global feature flags such as HNS, Google auth, atomic rename, new reader, standard symlinks, and unsupported path support.

Control flow and integration: each test builds a fresh command, sets arguments, executes `PersistentPreRunE`, and captures `mountInfo.config` from the fake mount callback. Config-file cases exercise Viper YAML loading, `cfg.DecodeHook`, strict `mapstructure` unused-field rejection, `cfg.ValidateConfig`, `ApplyOptimizations`, and `cfg.Rationalize`; CLI cases assert that explicit flags override config defaults and optimization rules.

State and persistence: tests create only temporary config files and process-local env overrides such as `GCSFUSE_IN_BACKGROUND_MODE`. No mount, GCS, or filesystem state is persisted, but the tests assert the derived `mountInfo` fields that later drive real mounting and config logging.

Dependencies: Go testing, testify assertions, Cobra/pflag argument parsing, Viper config state, `cfg` defaults/validators/decode hooks, path resolution, runtime CPU count for defaults, and platform home/current directories.

Risks: this file is a high-signal compatibility net; flag rename, default drift, new schema fields, optimization-rule changes, and validation-message changes can break many cases. Tests that rely on runtime CPU count or home/current directories should stay value-normalized. Because it focuses on parsing, it does not prove the mounted filesystem honors every parsed value.

Test signals: run `go test ./cmd -run TestArgsParsing`, `go test ./cmd -run TestMountInfoPopulation`, and targeted datatype/config validation tests when changing `cfg` schema, default values, rationalization, or root command wiring.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/root_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/bool1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/bool1.yaml

Purpose: boolean true decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `foreground`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `foreground: true` to exercise boolean unmarshalling. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/bool1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/bool2.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/bool2.yaml

Purpose: boolean false decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `foreground`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `foreground: false` to exercise boolean unmarshalling. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/bool2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/duration1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/duration1.yaml

Purpose: zero duration decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `http-client-timeout`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets HTTP client timeout to numeric zero. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/duration1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/duration2.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/duration2.yaml

Purpose: seconds duration decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `http-client-timeout`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets HTTP client timeout to `15s`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/duration2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/duration3.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/duration3.yaml

Purpose: compound duration decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `http-client-timeout`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets HTTP client timeout to `1h15s`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/duration3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/duration4.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/duration4.yaml

Purpose: negative duration decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `http-client-timeout`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets HTTP client timeout to `-1h15s`, exercising signed duration parsing. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/duration4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/empty_file.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/empty_file.yaml

Purpose: empty config fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with no explicit keys. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It contains no YAML keys and is used to verify defaults for config-file driven tests. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/empty_file.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_download_chunk_size_mb.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_download_chunk_size_mb.yaml

Purpose: negative file-cache validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-cache`, `cache-file-for-range-read`, `parallel-downloads-per-file`, `download-chunk-size-mb`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It drives `isValidFileCacheConfig` to reject a zero `download-chunk-size-mb`, whose minimum is 1. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: config validation should return the download-chunk-size error before mount execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_download_chunk_size_mb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_max_parallel_downloads.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_max_parallel_downloads.yaml

Purpose: negative parallel-download configuration fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-cache`, `cache-file-for-range-read`, `enable-parallel-downloads`, `parallel-downloads-per-file`, `max-parallel-downloads`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies negative `max-parallel-downloads` is rejected while parallel downloads are enabled. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: config validation should surface the max-parallel-downloads lower-bound error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_max_parallel_downloads.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_max_size_mb.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_max_size_mb.yaml

Purpose: negative file-cache capacity fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `file-cache`, `max-size-mb`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies `max-size-mb` values below -1 are rejected even when write settings otherwise enable file-cache-related behavior. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: config validation should surface `max-size-mb` lower-bound failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_max_size_mb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_parallel_downloads_per_file.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_parallel_downloads_per_file.yaml

Purpose: negative per-file download fanout fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-cache`, `cache-file-for-range-read`, `parallel-downloads-per-file`, `max-parallel-downloads`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies `parallel-downloads-per-file` must be at least 1. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: config validation should reject the per-file parallel download count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_parallel_downloads_per_file.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_write_buffer_size.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_write_buffer_size.yaml

Purpose: negative parallel-download write-buffer fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `file-cache`, `enable-parallel-downloads`, `max-size-mb`, `write-buffer-size`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables parallel downloads and provides a write buffer below or not aligned to the 4096-byte minimum. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: config validation should reject `write-buffer-size` before mount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_write_buffer_size.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_zero_max_parallel_downloads.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_zero_max_parallel_downloads.yaml

Purpose: negative zero max-parallel-downloads fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-cache`, `enable-parallel-downloads`, `max-parallel-downloads`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies enabled parallel downloads cannot use `max-parallel-downloads: 0`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: validation should return the explicit zero-max-parallel-downloads error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_zero_max_parallel_downloads.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_zero_write_buffer_size.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_zero_write_buffer_size.yaml

Purpose: negative parallel-download write-buffer fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `file-cache`, `enable-parallel-downloads`, `max-size-mb`, `write-buffer-size`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables parallel downloads and provides a write buffer below or not aligned to the 4096-byte minimum. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: config validation should reject `write-buffer-size` before mount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_zero_write_buffer_size.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_disable_parallel_dirops.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_disable_parallel_dirops.yaml

Purpose: negative filesystem boolean fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-system`, `disable-parallel-dirops`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It supplies a string where a boolean filesystem option is expected, exercising decode-hook/type errors. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: Viper/mapstructure unmarshalling should fail before mount execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_disable_parallel_dirops.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_ignore_interrupts.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_ignore_interrupts.yaml

Purpose: negative filesystem boolean fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-system`, `ignore-interrupts`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It supplies a string where a boolean filesystem option is expected, exercising decode-hook/type errors. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: Viper/mapstructure unmarshalling should fail before mount execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_ignore_interrupts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_kernel_list_cache_ttl.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_kernel_list_cache_ttl.yaml

Purpose: negative kernel list-cache TTL fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-system`, `kernel-list-cache-ttl-secs`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `kernel-list-cache-ttl-secs` below the accepted -1 sentinel. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: validation should reject the TTL lower bound.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/invalid_kernel_list_cache_ttl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unset_file_system_config.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unset_file_system_config.yaml

Purpose: file-system defaulting fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It omits the `file-system` subtree while setting an unrelated write flag, proving defaults survive absent nested config. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: root config parsing should succeed and preserve default filesystem values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unset_file_system_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unsupported_large_kernel_list_cache_ttl.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unsupported_large_kernel_list_cache_ttl.yaml

Purpose: oversized kernel list-cache TTL fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-system`, `kernel-list-cache-ttl-secs`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `kernel-list-cache-ttl-secs` above the supported int64-duration limit. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: validation should reject the TTL as too high.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unsupported_large_kernel_list_cache_ttl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/float1.yaml

Purpose: float sentinel fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `limit-bytes-per-sec`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `limit-bytes-per-sec: -1`, the unlimited sentinel. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float2.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/float2.yaml

Purpose: positive integer-as-float fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `limit-bytes-per-sec`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `limit-bytes-per-sec: 1`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float3.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/float3.yaml

Purpose: zero float fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `limit-bytes-per-sec`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `limit-bytes-per-sec: 0`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float4.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/float4.yaml

Purpose: positive fractional float fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `limit-bytes-per-sec`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `limit-bytes-per-sec: 12.5`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float5.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/float5.yaml

Purpose: negative fractional float fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `limit-bytes-per-sec`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `limit-bytes-per-sec: -12.5`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float5.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/invalid_anonymous_access.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/invalid_anonymous_access.yaml

Purpose: negative GCS auth boolean fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-auth`, `anonymous-access`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It gives `anonymous-access` a non-boolean value to exercise strict type decoding. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: unmarshal should fail for invalid boolean input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/invalid_anonymous_access.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/unset_anonymous_access.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/unset_anonymous_access.yaml

Purpose: GCS auth defaulting fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It omits `gcs-auth` while setting an unrelated write flag, proving auth defaults remain in effect. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: root config parsing should succeed with default anonymous-access false.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/unset_anonymous_access.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_increase_rate_negative.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_increase_rate_negative.yaml

Purpose: negative read-stall retry tuning fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-retries`, `read-stall`, `enable`, `min-req-timeout`, `max-req-timeout`, `initial-req-timeout`, `req-increase-rate`, `req-target-percentile`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables read-stall retries and sets `req-increase-rate` negative. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: validation should reject enabled read-stall retry parameters outside their allowed ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_increase_rate_negative.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_increase_rate_zero.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_increase_rate_zero.yaml

Purpose: negative read-stall retry tuning fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-retries`, `read-stall`, `enable`, `min-req-timeout`, `max-req-timeout`, `initial-req-timeout`, `req-increase-rate`, `req-target-percentile`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables read-stall retries and sets `req-increase-rate` to zero. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: validation should reject enabled read-stall retry parameters outside their allowed ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_increase_rate_zero.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_target_percentile_large.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_target_percentile_large.yaml

Purpose: negative read-stall retry tuning fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-retries`, `read-stall`, `enable`, `min-req-timeout`, `max-req-timeout`, `initial-req-timeout`, `req-increase-rate`, `req-target-percentile`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables read-stall retries and sets `req-target-percentile` above the open interval upper bound. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: validation should reject enabled read-stall retry parameters outside their allowed ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_target_percentile_large.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_target_percentile_negative.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_target_percentile_negative.yaml

Purpose: negative read-stall retry tuning fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-retries`, `read-stall`, `enable`, `min-req-timeout`, `max-req-timeout`, `initial-req-timeout`, `req-increase-rate`, `req-target-percentile`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables read-stall retries and sets `req-target-percentile` negative. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: validation should reject enabled read-stall retry parameters outside their allowed ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_retries/read_stall/invalid_req_target_percentile_negative.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/empty.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/empty.yaml

Purpose: config-file flag extraction empty fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with no explicit keys. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It confirms `getConfigFileFlags` returns an empty map for an empty file instead of Viper defaults. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should compare an empty map, not defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/empty.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/nested_values.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/nested_values.yaml

Purpose: config-file flag extraction nested fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `logging`, `file-path`, `format`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies nested YAML maps are preserved for logging config-file-provided flags. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should return a nested `logging` map with file path and format.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/nested_values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/simple_values.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/simple_values.yaml

Purpose: config-file flag extraction scalar fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `key1`, `key2`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies scalar values are returned from the raw config file without injected defaults. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should return only key1/key2 from the file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/simple_values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/int1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/int1.yaml

Purpose: integer zero fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `logging`, `log-rotate`, `backup-file-count`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets log rotation `backup-file-count: 0`, the retain-all sentinel. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/int1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/int2.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/int2.yaml

Purpose: integer sentinel fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `max-conns-per-host`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `max-conns-per-host: -1`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/int2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/int3.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/int3.yaml

Purpose: positive integer fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `max-conns-per-host`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `max-conns-per-host: 12`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/int3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_config.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_config.yaml

Purpose: unexpected top-level field fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `a`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It contains unknown key `a` to verify strict unused-field rejection. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_config.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_config.yaml

Purpose: invalid log severity fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `logging`, `severity`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets logging severity to unsupported `critical`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_rotate_config_1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_rotate_config_1.yaml

Purpose: invalid log-rotate bounds fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `logging`, `severity`, `log-rotate`, `max-file-size-mb`, `backup-file-count`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets negative max file size and backup file count. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_rotate_config_1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_rotate_config_2.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_rotate_config_2.yaml

Purpose: invalid log-rotate backup fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `logging`, `severity`, `log-rotate`, `backup-file-count`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets negative backup file count. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_log_rotate_config_2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_metrics_config_both_set.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_metrics_config_both_set.yaml

Purpose: cloud metrics interval fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `metrics`, `stackdriver-export-interval`, `cloud-metrics-export-interval-secs`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `cloud-metrics-export-interval-secs` to a positive value. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: metrics config parsing should preserve the interval.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_metrics_config_both_set.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_profile.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_profile.yaml

Purpose: invalid profile fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `profile`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets an unsupported profile name. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_profile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_unexpectedfield_config.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_unexpectedfield_config.yaml

Purpose: unexpected nested field fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `logging`, `formats`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It uses `logging.formats` instead of `logging.format` to verify strict schema enforcement. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/invalid_unexpectedfield_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/logseverity1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/logseverity1.yaml

Purpose: uppercase log severity fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `logging`, `severity`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets severity `TRACE`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/logseverity1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/logseverity2.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/logseverity2.yaml

Purpose: lowercase log severity fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `logging`, `severity`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets severity `trace` to verify case normalization. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/logseverity2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_stat-cache-max-size-mb.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_stat-cache-max-size-mb.yaml

Purpose: negative metadata-cache validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `metadata-cache`, `stat-cache-max-size-mb`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `stat-cache-max-size-mb` below the -1 sentinel. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: metadata cache validation should reject the configured limit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_stat-cache-max-size-mb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_ttl.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_ttl.yaml

Purpose: negative metadata-cache validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `metadata-cache`, `ttl-secs`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `ttl-secs` below the -1 sentinel. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: metadata cache validation should reject the configured limit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_ttl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_type-cache-max-size-mb.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_type-cache-max-size-mb.yaml

Purpose: negative metadata-cache validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `metadata-cache`, `type-cache-max-size-mb`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `type-cache-max-size-mb` below the -1 sentinel. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: metadata cache validation should reject the configured limit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_invalid_type-cache-max-size-mb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_stat-cache-max-size-mb_too_high.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_stat-cache-max-size-mb_too_high.yaml

Purpose: negative metadata-cache validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `metadata-cache`, `stat-cache-max-size-mb`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `stat-cache-max-size-mb` just above the supported maximum. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: metadata cache validation should reject the configured limit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_stat-cache-max-size-mb_too_high.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_ttl_too_high.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_ttl_too_high.yaml

Purpose: negative metadata-cache validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `metadata-cache`, `ttl-secs`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `ttl-secs` just above the supported max duration in seconds. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: metadata cache validation should reject the configured limit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metadata_cache/metadata_cache_config_ttl_too_high.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/empty.yml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/empty.yml

Purpose: metrics defaults fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with no explicit keys. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It leaves metrics unset to verify default worker, buffer, exporter, and interval behavior. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: metrics config parsing should succeed with defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/empty.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/metrics_export_interval_positive.yml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/metrics_export_interval_positive.yml

Purpose: cloud metrics interval fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `metrics`, `cloud-metrics-export-interval-secs`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `cloud-metrics-export-interval-secs` to a positive value. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: metrics config parsing should preserve the interval.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/metrics_export_interval_positive.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/stackdriver_export_interval_positive.yml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/stackdriver_export_interval_positive.yml

Purpose: legacy stackdriver interval fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `metrics`, `stackdriver-export-interval`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `stackdriver-export-interval` so rationalization can fill cloud metrics seconds. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should observe equivalent duration/seconds values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/metrics_config/stackdriver_export_interval_positive.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/empty.yml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/empty.yml

Purpose: trace defaults fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with no explicit keys. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It leaves trace config unset to verify default exporter and sampling behavior. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: trace config parsing should succeed with defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/empty.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/sanitize_trace_exporters.yml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/sanitize_trace_exporters.yml

Purpose: trace exporter normalization fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `trace`, `exporters`, `sampling-ratio`, `project-id`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It uses mixed-case comma-separated trace exporters and a sampling ratio/project to verify sanitizer behavior. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: trace parsing should normalize exporters to gcpexporter/stdout and keep sampling/project.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/sanitize_trace_exporters.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/cli_override_config.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/cli_override_config.yaml

Purpose: mount-info CLI override fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `app-name`, `file-system`, `gid`, `logging`, `severity`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It supplies config-file app name, gid, and log severity while tests pass CLI overrides for selected fields. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: mountInfo should record both config-file flags and effective CLI-overridden config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/cli_override_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/config_file_only.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/config_file_only.yaml

Purpose: mount-info config-only fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `app-name`, `file-system`, `gid`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It supplies app name and gid only through config file for mountInfo logging capture. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: mountInfo should report config-file flags and resolved config values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/config_file_only.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/octal1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/octal1.yaml

Purpose: octal decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-system`, `file-mode`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets file mode string `765` for octal parsing. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/octal1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/protocol1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/protocol1.yaml

Purpose: protocol decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `client-protocol`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets client protocol `http2`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/protocol1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/empty.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/empty.yaml

Purpose: read config default fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with no explicit keys. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It omits read settings to verify default inactive stream timeout. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should observe the default 10s timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/empty.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/override.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/override.yaml

Purpose: read timeout override fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `read`, `inactive-stream-timeout`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It overrides `read.inactive-stream-timeout` to 30s. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should observe the parsed duration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/override.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/override_with_grpc.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/override_with_grpc.yaml

Purpose: read timeout with grpc fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `read`, `inactive-stream-timeout`, `gcs-connection`, `client-protocol`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets read inactive timeout and gRPC client protocol to verify read timeout parsing is independent of protocol. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should observe 30s inactive timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/read_config/override_with_grpc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/resolvedpath1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/resolvedpath1.yaml

Purpose: resolved path fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `cache-dir`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `cache-dir: /home`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/resolvedpath1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/string1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/string1.yaml

Purpose: string decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `app-name`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `app-name: abc`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/string1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/stringslice1.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/stringslice1.yaml

Purpose: string slice decode fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-system`, `fuse-options`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets three FUSE options as YAML list entries. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/stringslice1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/test_creds.json -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/test_creds.json

Purpose: service-account credential JSON fixture for gcsfuse command/config tests.

Important data and APIs: JSON fixture data with no explicit keys. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It contains placeholder service-account fields for key-file path/decode tests without real secret material. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/test_creds.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/unset_machine_type.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/unset_machine_type.yaml

Purpose: machine type defaulting fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `disable-autoconfig`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It disables autoconfig without setting machine type. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/unset_machine_type.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/valid_config.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/valid_config.yaml

Purpose: full valid config fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `app-name`, `read`, `inactive-stream-timeout`, `enable-buffered-read`, `global-max-blocks`, `block-size-mb`, `start-blocks-per-handle`, `max-blocks-per-handle`, `min-blocks-per-handle`, `random-seek-threshold`, `write`, `create-empty-file`, `enable-streaming-writes`, `max-blocks-per-file`, `enable-rapid-appends`, `file-cache`, `cache-file-for-range-read`, `download-chunk-size-mb`, `enable-crc`, `enable-parallel-downloads`, `max-parallel-downloads`, `max-size-mb`, `parallel-downloads-per-file`, `write-buffer-size`, `enable-o-direct`, `experimental-disable-size-calculation-fix`, `gcs-auth`, `anonymous-access`, `key-file`, `reuse-token-from-url`, `token-url`, `gcs-connection`, `billing-project`, `client-protocol`, `custom-endpoint`, `experimental-enable-json-read`, `grpc-conn-pool-size`, `grpc-path-strategy`, `http-client-timeout`, `limit-bytes-per-sec`, `limit-ops-per-sec`, `max-conns-per-host`, `max-idle-conns-per-host`, `sequential-read-size-mb`, `gcs-retries`, `experimental-nonrapid-folder-api-stall-retry`, `chunk-retry-deadline-secs`, `chunk-transfer-timeout-secs`, `read-stall`, `enable`, `min-req-timeout`, `max-req-timeout`, `initial-req-timeout`, `req-increase-rate`, `req-target-percentile`, `file-system`, `dir-mode`, `disable-parallel-dirops`, `file-mode`, `fuse-options`, `gid`, `uid`, `ignore-interrupts`, `kernel-list-cache-ttl-secs`, `rename-dir-limit`, `temp-dir`, `max-read-ahead-kb`, `list`, `enable-empty-managed-folders`, `enable-hns`, `enable-atomic-rename-object`, `metadata-cache`, `deprecated-stat-cache-capacity`, `deprecated-stat-cache-ttl`, `deprecated-type-cache-ttl`, `enable-nonexistent-type-cache`, `metadata-prefetch-max-workers`, `enable-metadata-prefetch`, `metadata-prefetch-entries-limit`, `experimental-metadata-prefetch-on-mount`, `stat-cache-max-size-mb`, `ttl-secs`, `type-cache-max-size-mb`, `metrics`, `cloud-metrics-export-interval-secs`, `workers`, `buffer-size`, `machine-type`, `dummy-io`, `reader-latency`, `per-mb-latency`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It exercises most config subtrees with non-default valid values, including read/write/cache/auth/connection/retries/filesystem/list/metadata/metrics/dummy-io. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/valid_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/valid_config_with_0_backup-file-count.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/valid_config_with_0_backup-file-count.yaml

Purpose: valid log rotation retain-all fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `logging`, `file-path`, `format`, `severity`, `log-rotate`, `max-file-size-mb`, `backup-file-count`, `compress`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies backup-file-count zero is valid when log rotation settings are otherwise populated. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/valid_config_with_0_backup-file-count.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/valid_profile.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/valid_profile.yaml

Purpose: valid profile fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `profile`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets profile `aiml-training`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/valid_profile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/empty.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/empty.yaml

Purpose: workload insight defaults fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with no explicit keys. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It omits workload insight settings to verify visualization defaults are disabled. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should observe visualize false and empty output path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/empty.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/visual_with_output_file.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/visual_with_output_file.yaml

Purpose: workload insight output fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `workload-insight`, `visualize`, `output-file`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables visualization and provides an output HTML path. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should preserve both values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/visual_with_output_file.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/visual_without_output_file.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/visual_without_output_file.yaml

Purpose: workload insight visualize-only fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `workload-insight`, `visualize`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables visualization without an output file to test partial nested config. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should observe visualize true and empty output path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/workload_insight_config/visual_without_output_file.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_0_block_size.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_0_block_size.yaml

Purpose: negative streaming write validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `enable-streaming-writes`, `block-size-mb`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables streaming writes with `block-size-mb: 0`, below the valid minimum. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: write config validation should reject the invalid streaming write bound.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_0_block_size.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_invalid_global_max_blocks.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_invalid_global_max_blocks.yaml

Purpose: negative streaming write validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `enable-streaming-writes`, `global-max-blocks`, `block-size-mb`, `max-blocks-per-file`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables streaming writes with `global-max-blocks: -2`, below the -1 sentinel. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: write config validation should reject the invalid streaming write bound.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_invalid_global_max_blocks.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_zero_max_blocks_per_file.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_zero_max_blocks_per_file.yaml

Purpose: negative streaming write validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `enable-streaming-writes`, `global-max-blocks`, `block-size-mb`, `max-blocks-per-file`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables streaming writes with `max-blocks-per-file: 0`, below the valid positive or -1 choices. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: write config validation should reject the invalid streaming write bound.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_zero_max_blocks_per_file.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/queue.go -->
# Research: sources/user-network-fs/gcsfuse/common/queue.go

Purpose: defines a small generic FIFO queue abstraction and linked-list implementation used by buffered read prefetching to track ordered block work.

Important APIs/types/functions: `Queue[T]` exposes `IsEmpty`, `Peek`, `Push`, `Pop`, and `Len`; `NewLinkedListQueue[T]` returns a `linkedListQueue[T]`; private `node[T]` links items through `start` and `end` pointers with a `size` counter.

Control flow: `Push` appends at the tail and initializes both ends for the first element. `Peek` returns the head without mutation. `Pop` removes the head, resets both pointers when the final element is removed, and decrements length. `Peek` and `Pop` intentionally panic on empty queues.

State and persistence: state is entirely in memory and not synchronized. Queue ordering and `size` are the invariants; no persistence or external resources are involved.

Dependencies: only Go generics and package-local structs. The current major integration point is `internal/bufferedread.BufferedReader.blockQueue`.

Risks: not thread-safe; callers must lock externally. Empty-queue panics are correct for misuse but require callers to guard with `IsEmpty`. If used with mutable pointer values, queue ownership is not copied.

Test signals: `common/queue_test.go` covers construction, FIFO behavior, length, peek non-mutation, empty state, and panics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/queue_test.go -->
# Research: sources/user-network-fs/gcsfuse/common/queue_test.go

Purpose: unit tests for the generic linked-list queue implementation.

Important APIs/types/functions: tests call `NewLinkedListQueue[int]`, `Push`, `Peek`, `Pop`, `Len`, and `IsEmpty`, with testify assertions and panic checks.

Control flow: cases build queues, enqueue several integers, verify FIFO pop order, verify `Peek` leaves length unchanged, and assert that empty `Pop` and `Peek` panic.

State and persistence: all state is in-memory queue state scoped to each test; no external files or global state.

Dependencies: Go testing plus `github.com/stretchr/testify/assert` and `require`.

Risks: tests do not exercise concurrent access because the queue is intentionally unsynchronized. They also do not test pointer payload aliasing, but that is outside queue ownership.

Test signals: run `go test ./common -run LinkedListQueue`; failures indicate a FIFO invariant or panic-contract change.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/queue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/util.go -->
# Research: sources/user-network-fs/gcsfuse/common/util.go

Purpose: shared utility helpers for shutdown composition, Linux kernel-version probing, kernel-list-cache feature gating, and small file read/write helpers.

Important APIs/types/functions: `ShutdownFn`, `JoinShutdownFunc`, `GetKernelVersion`, `kernelVersionToTest`, `IsKLCacheEvictionUnSupported`, `CloseFile`, `WriteFile`, and `ReadFile`.

Control flow: `JoinShutdownFunc` runs non-nil shutdown callbacks in order and accumulates errors with `errors.Join`. Kernel detection shells out to `uname -r`, then regex-matches unsupported 6.9 through 6.12 kernel series. File helpers open paths, defer `CloseFile`, and use `WriteAt` or `os.ReadFile`.

State and persistence: `kernelVersionToTest` is a package variable deliberately replaceable in tests. `WriteFile` mutates an existing file from offset zero; it does not truncate trailing content. `CloseFile` calls `log.Fatalf` on close failure, which exits the process.

Dependencies: context, errors, regexp, `os/exec`, `os`, and process kernel reporting. Integration points include tests and features deciding whether kernel list cache eviction is supported.

Risks: hard-coded unsupported kernel regexes can age quickly. `WriteFile` requires an existing file and may leave stale bytes if new content is shorter. Fatal close behavior is harsh for library-style use. `GetKernelVersion` is Linux-specific.

Test signals: `util_test.go` mocks `kernelVersionToTest`, checks joined error contents, and validates temporary file read/write helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/util_test.go -->
# Research: sources/user-network-fs/gcsfuse/common/util_test.go

Purpose: tests shared common utilities for kernel feature gating, shutdown composition, and file helpers.

Important APIs/types/functions: `TestIsKLCacheEvictionUnSupported`, `TestJoinShutdownFunc`, `TestCloseFile`, `TestWriteFile`, and `TestReadFile`.

Control flow: kernel tests replace `kernelVersionToTest` per case and restore it. Shutdown tests run in parallel and assert joined errors contain each expected message. File tests create temp files, write/read content, and close them.

State and persistence: uses temporary files and a mutable package variable. The kernel-version mock is restored with `defer` to prevent cross-test contamination.

Dependencies: Go testing, testify, temp filesystem access, and the utility functions under test.

Risks: the kernel-version test is table-driven but only covers current unsupported ranges. File-helper tests do not check shorter overwrite truncation behavior or fatal close failure.

Test signals: `go test ./common`; failures indicate regression in feature-gate regexes, error joining, or file helper behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/version.go -->
# Research: sources/user-network-fs/gcsfuse/common/version.go

Purpose: centralizes the displayed gcsfuse version string.

Important APIs/types/functions: package variable `gcsfuseVersion` is set at build time with `-ldflags -X`; `GetVersion` returns the injected value or `unknown` plus the current Go runtime version.

Control flow: `GetVersion` checks for an empty injected version, substitutes `unknown`, and formats it with `runtime.Version()`.

State and persistence: no persistent state. The only mutable state is the package variable populated by build tooling.

Dependencies: `fmt`, `runtime`, and release tooling such as `tools/build_gcsfuse`.

Risks: missing linker injection makes binaries report `unknown`; callers that parse this human string must handle the appended Go version.

Test signals: release builds should assert `gcsfuse --version` contains the intended product version and Go version.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/csi_driver_build.yml -->
# Research: sources/user-network-fs/gcsfuse/csi_driver_build.yml

Purpose: Google Cloud Build pipeline for building gcsfuse binaries and embedding them into a GCS Fuse CSI Driver image.

Important data/APIs: substitutions define Go version, gcsfuse version, CSI driver branch, ARM build toggle, image owner/prefix, and optional staging version. Steps clone `GoogleCloudPlatform/gcs-fuse-csi-driver`, run `tools/build_gcsfuse/main.go`, create a temporary GCS bucket, upload linux architecture artifacts, build/push the CSI driver image with `make build-image-and-push-multi-arch`, and remove the temporary bucket.

Control flow: clone, build, and bucket creation start concurrently. Binary upload waits for build and bucket creation; image build waits for upload and clone; cleanup waits for image build.

State and persistence: persistent outputs are pushed container images and uploaded artifacts consumed during the same build. Temporary state includes `/workspace/gcsfuse-artifacts`, `/workspace/bucket_name`, `csi-driver-src`, and a short-lived GCS bucket.

Dependencies: Cloud Build, git, golang image, gcloud storage, docker builder, apt package installation inside the docker step, GCR auth, CSI driver Makefile targets, and project IAM permissions for bucket/image operations.

Risks: cleanup runs only after successful image build, so failed builds may leave temporary buckets. The docker step installs cloud SDK dynamically, increasing network/time fragility. Branch/version substitutions control supply-chain inputs and should be pinned for release builds.

Test signals: dry-run Cloud Build with `_BUILD_ARM=false` and true, verify artifacts under both linux arches, image tags, bucket cleanup, and CSI driver image can find the staged gcsfuse binaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/csi_driver_build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/auth.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/auth.go

Purpose: legacy OAuth2 token-source construction for GCS access, supporting service account key files, external token endpoints, ADC, and non-default universe domains.

Important APIs/types/functions: `UniverseDomainDefault`, `getUniverseDomain`, `newTokenSourceFromPath`, and `GetTokenSource`.

Control flow: `GetTokenSource` chooses key-file, token-url, or Google default token source. Key-file flow reads JSON, builds a JWT config, obtains universe domain through `google.CredentialsFromJSON`, and switches to self-signed JWT access tokens when the domain is not `googleapis.com`.

State and persistence: no persistent state; it reads credential files and returns token-source objects that may cache/reuse tokens depending on the underlying oauth2 implementation.

Dependencies: `golang.org/x/oauth2/google`, storage v1 full-control scope, local files, context, and the package's proxy token-source helper.

Risks: key files are sensitive; errors include file paths and parsing context. Non-default universe domain handling depends on Google library semantics. When both key-file and token-url are supplied, key-file wins.

Test signals: `auth_test.go` covers universe-domain extraction for Google, TPC, and invalid JSON; token-url behavior is covered in `token_source_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/auth_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/auth_test.go

Purpose: validates universe-domain extraction used by key-file token-source selection.

Important APIs/types/functions: `AuthTest` testify suite, `TestGetUniverseDomainForGoogle`, `TestGetUniverseDomainForTPC`, and `TestGetUniverseDomainForEmptyCreds`.

Control flow: tests read fixture JSON files, call private `getUniverseDomain`, and assert either default `googleapis.com`, TPC `apis-tpclp.goog`, or a wrapped JSON parse error.

State and persistence: fixture-only reads; no external token exchange or credential persistence.

Dependencies: storage full-control scope, oauth2/google credential parsing, testify suite/assertions, and JSON fixtures under `internal/auth/testdata`.

Risks: fixture private keys are placeholders, but schema must remain parseable by Google libraries. Exact error-string assertions may drift with dependency upgrades.

Test signals: run `go test ./internal/auth -run AuthSuite` after changing credential parsing or universe-domain support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/credentials.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/credentials.go

Purpose: newer cloud auth credentials discovery path using `cloud.google.com/go/auth/credentials`.

Important APIs/types/functions: package `scope` is `storage.ScopeFullControl`; private `getCredentials` builds `credentials.DetectOptions`; exported `GetCredentials` calls `credentials.DetectDefault`.

Control flow: caller-provided key file is passed as `CredentialsFile`; empty key file allows Application Default Credentials and metadata-server discovery. Errors are wrapped as credential-detection failures.

State and persistence: no persistent state; the returned `*auth.Credentials` may internally cache tokens according to the auth library.

Dependencies: Cloud auth library, Cloud Storage full-control scope, and environment/metadata server behavior in `DetectDefault`.

Risks: full-control scope is broad. ADC discovery can contact metadata services in real deployments. Key-file precedence and empty-string behavior are part of the public contract.

Test signals: `credentials_test.go` injects a mock detector to verify options and error wrapping without external services.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/credentials.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/credentials_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/credentials_test.go

Purpose: unit tests for credential discovery option construction and error wrapping.

Important APIs/types/functions: `MockDetectCredentials`, `Test_getCredentials_Success`, and `Test_getCredentials_Error`.

Control flow: a testify mock expects exact `credentials.DetectOptions` for key-file and ADC-style empty key-file cases, then returns either credentials or a simulated error.

State and persistence: no external credentials are read; tests use mocks only.

Dependencies: testify mock/assertions and cloud auth types.

Risks: exact struct matching can break if detect options gain default fields. The tests do not exercise real ADC metadata-server behavior.

Test signals: `go test ./internal/auth -run getCredentials`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/credentials_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/empty_creds.json -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/testdata/empty_creds.json

Purpose: empty credential fixture used to prove universe-domain extraction reports a wrapped JSON parse error.

Important data and APIs: the file is intentionally empty JSON input for `google.CredentialsFromJSON`; it is consumed by `auth_test.go` rather than runtime code.

Control flow and integration: `TestGetUniverseDomainForEmptyCreds` reads the file and calls private `getUniverseDomain`, expecting `CredentialsFromJSON(): unexpected end of JSON input`.

State and persistence: static test data only; no credentials or token state.

Dependencies: oauth2/google credential parser error behavior and exact error wrapping.

Risks: dependency upgrades can change the underlying error string. The fixture must remain empty to test the intended failure.

Test signals: `go test ./internal/auth -run TestAuthSuite/TestGetUniverseDomainForEmptyCreds`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/empty_creds.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/google_creds.json -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/testdata/google_creds.json

Purpose: service-account credential fixture representing the default Google universe domain.

Important data and APIs: placeholder service-account JSON includes `universe_domain: googleapis.com` along with key, client, token, and certificate URL fields required by Google credential parsing.

Control flow and integration: `auth_test.go` reads it and verifies `getUniverseDomain` returns `UniverseDomainDefault`, which keeps `newTokenSourceFromPath` on the normal OAuth2 JWT token-source path.

State and persistence: static non-secret test credential data; no token is fetched during the test.

Dependencies: oauth2/google JSON credential schema and storage scope handling.

Risks: placeholder private key formatting must remain parseable by the library. If default universe-domain behavior changes, the expected domain may need updating.

Test signals: `go test ./internal/auth -run TestAuthSuite/TestGetUniverseDomainForGoogle`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/google_creds.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/tpc_creds.json -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/testdata/tpc_creds.json

Purpose: service-account credential fixture for a non-default Trusted Partner Cloud universe domain.

Important data and APIs: placeholder credential JSON includes `universe_domain: apis-tpclp.goog`, allowing tests to distinguish TPC from normal Google domain credentials.

Control flow and integration: `auth_test.go` verifies `getUniverseDomain` returns the TPC domain. Runtime key-file auth uses this distinction to select self-signed JWT access tokens instead of normal token exchange.

State and persistence: static non-secret test data; no external token service is contacted.

Dependencies: oauth2/google credential parsing and universe-domain support.

Risks: if non-default universe-domain credential schema changes, the fixture can become stale. The test only validates domain extraction, not end-to-end TPC access.

Test signals: `go test ./internal/auth -run TestAuthSuite/TestGetUniverseDomainForTPC`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/tpc_creds.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/token_source.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/token_source.go

Purpose: token-source implementation backed by an HTTP or Unix-socket token endpoint, with optional oauth2 token reuse.

Important APIs/types/functions: `newProxyTokenSource`, `proxyTokenSource.Token`, and exported `NewTokenSourceFromURL`.

Control flow: URL parsing selects a normal HTTP client or a custom Unix-socket transport. `Token` performs GET, reads at most 1 MiB, converts non-2xx responses into `oauth2.RetrieveError`, and JSON-decodes the response into `oauth2.Token`.

State and persistence: the proxy source itself is stateless. If `reuseTokenFromUrl` is true, `oauth2.ReuseTokenSource` wraps it and caches valid tokens in memory.

Dependencies: net/http, net/url, Unix-socket dialing through `net.Dialer`, oauth2 token types, endpoint availability, and caller context at construction time.

Risks: `Token` uses `client.Get(ts.endpoint)` and does not pass the stored context into the request, so cancellation may not affect HTTP GETs. Endpoint responses are trusted to provide token JSON. The 1 MiB body limit avoids unbounded memory use but may truncate unusual errors.

Test signals: `token_source_test.go` covers successful HTTP token fetch, invalid URL, server error, and invalid JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/token_source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/token_source_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/token_source_test.go

Purpose: tests proxy token-source URL parsing and token-fetch error handling.

Important APIs/types/functions: `Test_NewTokenSourceFromURL_Success`, `Test_NewTokenSourceFromURL_InvalidURL`, `TestProxyTokenSource_TokenFetch_ServerError`, and `TestProxyTokenSource_TokenFetch_InvalidJSON`.

Control flow: httptest servers return token JSON, HTTP 500 text, or invalid JSON; tests construct a source and call `Token` to validate returned token or error contents.

State and persistence: in-memory httptest servers only; no real credentials or network services beyond loopback.

Dependencies: `httptest`, JSON encoder, oauth2 token type, testify.

Risks: tests do not cover Unix-socket URLs, reuse-token caching, body limit behavior, or request cancellation.

Test signals: run `go test ./internal/auth -run TokenSource`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/token_source_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/block.go

Purpose: memory-backed block abstraction for read/write buffering, implemented with mmap-backed byte slices.

Important APIs/types/functions: `Block` combines `io.ReadSeeker`, `io.Writer`, `GenBlock`, `Size`, and `Cap`; `memoryBlock` stores `buffer` and `readSeek`; `createBlock` allocates anonymous private mmap memory.

Control flow: `Write` appends data until capacity; `Read` copies from `readSeek` and returns EOF at the end; `Seek` supports start/current/end with bounds checks; `Reuse` clears data and read position; `Deallocate` munmaps the full capacity and nils the buffer.

State and persistence: state is process memory only, backed by OS virtual memory. Deallocation releases mmap resources; blocks returned to pools are reused after reset.

Dependencies: `syscall.Mmap/Munmap`, `io`, and external pool lifecycle management.

Risks: double deallocation or using a block after deallocation causes errors/panics or memory corruption risk. Large block sizes can fail mmap. The implementation is not synchronized.

Test signals: `block_test.go` covers writes, reads, seeking, capacity errors, reuse, and deallocation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block_pool.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/block_pool.go

Purpose: generic block pool with per-handle limits, reserved blocks, and a global semaphore limiting total mmap-backed memory blocks across readers/writers.

Important APIs/types/functions: `GenBlock`, `GenBlockPool[T]`, `CantAllocateAnyBlockError`, `NewGenBlockPool`, `Get`, `TryGet`, `Release`, `ClearFreeBlockChannel`, `TotalFreeBlocks`, `NewBlockPool`, and `NewPrefetchBlockPool`.

Control flow: construction validates sizes and reserves global semaphore permits. `TryGet` reuses from the free channel or creates a block if limits allow; `Get` loops until reuse/allocation becomes possible. `canAllocateBlock` enforces max blocks and semaphore availability outside reserved slots. Clearing deallocates free blocks and releases permits.

State and persistence: state is in-memory counters, free-block channel, and semaphore permits. Underlying blocks hold mmap memory until deallocated.

Dependencies: `golang.org/x/sync/semaphore`, concrete block factory functions, and callers providing external synchronization; comments explicitly mark the pool as not thread-safe.

Risks: incorrect semaphore release around reserved blocks can leak or over-release global capacity. `Get` can spin/block indefinitely when limits are exhausted and no block is released. Concurrent access without locks can leak memory.

Test signals: `block_pool_test.go` heavily covers config validation, reuse/allocation, blocking behavior, reserved blocks, global limit interactions, and cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block_pool_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/block_pool_test.go

Purpose: test suite for generic block pool resource accounting and allocation behavior.

Important APIs/types/functions: testify `BlockPoolTest`, `NewGenBlockPool`, `TryGet`, `Get`, `canAllocateBlock`, `ClearFreeBlockChannel`, helper methods that assert `Get` blocks or succeeds, and semaphore state checks.

Control flow: cases cover invalid block/max/reserved values, allocation from free blocks, mmap failure for huge blocks, blocking when local/global limits are reached, global semaphore acquisition/release, multiple pools sharing one semaphore, and reserved-block cleanup behavior.

State and persistence: tests allocate mmap-backed blocks and must return/deallocate them through pool clearing. State is process-local but tied to OS virtual-memory resources.

Dependencies: testify suite, semaphore, timers for blocking assertions, and the real `createBlock` allocator.

Risks: timer-based blocking checks can be slow or flaky under extreme scheduler pressure. Some tests mutate internal fields directly to exercise edge states.

Test signals: `go test ./internal/block -run BlockPoolTestSuite`; failures point to memory limit, semaphore, or cleanup regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block_pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/block_test.go

Purpose: tests the mmap-backed `memoryBlock` implementation.

Important APIs/types/functions: `MemoryBlockTest` suite exercises `createBlock`, `Write`, `Read`, `Seek`, `Reuse`, `Size`, `Cap`, and `Deallocate`.

Control flow: cases validate normal and over-capacity writes, multiple writes, empty reads, read EOF behavior, seek modes and invalid bounds, capacity reporting, reuse clearing, deallocation, and double deallocation error handling.

State and persistence: tests allocate anonymous memory mappings and deallocate them; no files or persistent state.

Dependencies: testify suite and OS mmap behavior.

Risks: exact mmap error strings for huge allocations can be OS-dependent. Tests are single-threaded and do not cover concurrent block access.

Test signals: `go test ./internal/block -run MemoryBlockTestSuite`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/prefetch_block.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/prefetch_block.go

Purpose: extends memory blocks with absolute file offsets, readiness notification, status, reference counting, and efficient `ReaderFrom` support for buffered read prefetching.

Important APIs/types/functions: `BlockStatus`, `BlockState`, `PrefetchBlock`, `prefetchMemoryBlock`, `createPrefetchBlock`, `ReadAt`, `ReadAtSlice`, `AbsStartOff`, `SetAbsStartOff`, `AwaitReady`, `NotifyReady`, `IncRef`, `DecRef`, `RefCount`, and `ReadFrom`.

Control flow: created/reused blocks start in-progress with a one-shot notification channel and unset offset. Producers write data then `NotifyReady`; consumers `AwaitReady`, then read slices or copied bytes. Reference counts prevent returning blocks to the pool while FUSE still owns returned slices.

State and persistence: all state is in memory. The backing buffer is mmap memory inherited from `memoryBlock`; readiness and ref-count fields are reset on reuse.

Dependencies: context cancellation for waits, atomic ref-counting, syscall mmap, and buffered-reader lifecycle rules that call notify exactly once.

Risks: double `NotifyReady` panics or blocks; `AbsStartOff` panics before initialization; `DecRef` panics on imbalance. Returned slices must not be mutated and require callback-based lifetime management.

Test signals: `prefetch_block_test.go` covers read bounds, offset setting, notification variants, cancellation, ref counting, and `ReadFrom` edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/prefetch_block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/prefetch_block_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/prefetch_block_test.go

Purpose: tests `PrefetchBlock` behavior for buffered-read blocks.

Important APIs/types/functions: `PrefetchMemoryBlockTest`, `createPrefetchBlock`, `ReadAt`, `ReadAtSlice`, `SetAbsStartOff`, `AbsStartOff`, `AwaitReady`, `NotifyReady`, `IncRef`, `DecRef`, and `ReadFrom`.

Control flow: tests fill blocks, assert slice/copy reads and EOF handling, validate negative/out-of-bounds offsets, exercise one-shot readiness notification with cancellation and multiple waiters, verify ref-count panic cases, and feed readers with short, long, empty, partial, and erroring streams.

State and persistence: process-local mmap-backed buffers and goroutines/channels for readiness tests; no persistent state.

Dependencies: context cancellation, testify suite, and small helper readers.

Risks: asynchronous notification tests depend on goroutine scheduling. The suite does not exercise integration with the workerpool or FUSE callback lifetime.

Test signals: `go test ./internal/block -run PrefetchMemoryBlockTestSuite`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/prefetch_block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/block_queue_entry.go -->
# Research: sources/user-network-fs/gcsfuse/internal/bufferedread/block_queue_entry.go

Purpose: small buffered-read queue entry tying a prefetch block to its cancel function and eviction state.

Important APIs/types/functions: `blockQueueEntry` contains a `block.PrefetchBlock`, `context.CancelFunc`, and `wasEvicted`; `cancelAndWait` cancels an in-flight download and waits for the block notification.

Control flow: cancellation triggers the download context, then `AwaitReady(context.Background())` waits for producer completion. Unexpected wait errors or non-canceled status errors are logged as warnings.

State and persistence: per-entry in-memory state. `wasEvicted` defers pool return until outstanding slice references release through callbacks.

Dependencies: `internal/block`, context, `internal/logger`, and buffered-reader download-task semantics that always notify readiness.

Risks: if a worker never calls `NotifyReady`, `cancelAndWait` can block. Calling `AbsStartOff` in warning paths assumes the block offset was set. Correct use depends on queue operations holding the buffered-reader lock.

Test signals: integration is covered through buffered-reader tests; direct unit tests would mock a block that reports cancellation and unexpected errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/block_queue_entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader.go -->
# Research: sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader.go

Purpose: implements a prefetching `gcsx.Reader` that serves sequential reads from mmap-backed in-memory blocks and falls back for random or memory-constrained access patterns.

Important APIs/types/functions: `BufferedReadConfig`, `BufferedReader`, `BufferedReaderOptions`, `NewBufferedReader`, `ReaderName`, `ReadAt`, `Destroy`, `CheckInvariants`, and helpers `handleRandomRead`, `prepareQueueForOffset`, `freshStart`, `prefetch`, `scheduleNextBlock`, `scheduleBlockWithIndex`, `callback`, and `releaseOrMarkEvicted`.

Control flow: construction reserves per-handle blocks from a global semaphore and initializes queue/pool state. `ReadAt` detects random seeks, clears stale queued blocks, starts urgent prefetch if needed, waits for the head block, returns zero-copy data slices plus a callback, and schedules more blocks as consumption advances. Random reads beyond threshold return `gcsx.FallbackToAnotherReader`; memory pressure during urgent block acquisition also falls back.

State and persistence: state is process-local and guarded by `mu`: block queue, block pool, next prefetch index, random seek count, prefetch window size, worker pool, and outstanding callback waitgroup. No data is persisted; downloaded ranges live in mmap blocks until returned to the pool or deallocated in `Destroy`.

Dependencies: common queue, block/prefetch pool, workerpool tasks, GCS bucket/object interfaces, metrics, tracing, read-type classifier, FUSE handle IDs, global semaphore, and `downloadTask` for actual object range reads.

Risks: zero-copy slices require FUSE callbacks to fire; otherwise `Destroy` may time out and leak blocks. Queue and pool are not thread-safe outside the reader lock. Cancellation relies on download tasks notifying block readiness. Random-read fallback thresholds and invariant `randomSeekCount <= threshold` must stay aligned.

Test signals: `buffered_reader_test.go` covers construction, reserved blocks, allocation failure, read paths, random read fallback, cleanup, and callback release behavior; `download_task_test.go` covers worker download status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader.go -->
