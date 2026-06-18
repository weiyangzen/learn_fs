# sources/compression/zstd/tests/regression/config.c

Purpose: This module defines the compression-configuration matrix used by the regression harness. It expands level macros from `levels.h` into `config_t` objects covering normal levels, negative fast levels, dictionary variants, row-match-finder settings, multithreading, long-distance mode, literal-compression modes, explicit frame/compression parameters, and pledged-source-size behavior.

Important APIs, types, and functions: It exports `configs`, a NULL-terminated array of `config_t const*`. `config_skip_data()` skips dictionary-only configs for data without dictionaries. `config_get_level()` extracts `ZSTD_c_compressionLevel` or returns `CONFIG_NO_LEVEL`. `config_get_zstd_params()` derives `ZSTD_parameters` from a config, source size, and dictionary size, then overlays selected C parameters and frame parameters.

Control flow: Macro families `FAST_LEVEL`, `LEVEL`, and `ROW_LEVEL` declare static `param_value_t` arrays and corresponding `config_t` instances. `levels.h` is included twice: once to generate definitions and once to populate `g_configs`. Additional static configs cover no pledged size, LDM, MT, small logs, explicit params, and literal modes. At runtime, callers iterate the exported array, optionally skip invalid data/config combinations, and pass the config to compression methods.

State and persistence: The matrix is static read-only configuration. No runtime state is mutated except the harness's iteration through these objects. Parameter arrays are file-scope and live for the process lifetime.

Dependencies and integration points: Depends on `config.h`, zstd static-only parameter enums, `levels.h`, and `data_has_dict()`. It is consumed by `test.c` and `method.c`. The string `cli_args` field must remain compatible with the CLI tested by `method.c`, while `param_values` must remain compatible with the advanced API paths.

Risks and test signals: The macro expansion is broad, so adding a level can multiply the test matrix substantially. `config_get_zstd_params()` handles only a subset of `ZSTD_cParameter` values; advanced-only parameters such as workers or row finder may be applied by other method paths but not reflected in legacy `ZSTD_parameters`. CLI and API parameter equivalence can drift. Expected signals are stable result-table rows and skips for unsupported combinations rather than compression errors.
