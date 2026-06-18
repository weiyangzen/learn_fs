# sources/compression/zstd/tests/regression/config.h

Purpose: This header defines the regression harness's compression configuration contract. It gives `method.c` and `test.c` a uniform way to identify a test configuration, provide equivalent CLI arguments and API parameters, and decide whether dictionary or pledged-size behavior applies.

Important APIs and types: `param_value_t` pairs a `ZSTD_cParameter` with an integer value. `param_values_t` wraps an array and size. `config_t` includes `name`, optional `cli_args`, `param_values`, and boolean fields `use_dictionary`, `no_pledged_src_size`, and `advanced_api_only`. `CONFIG_NO_LEVEL` is a sentinel below the valid compression-level range. Public functions are `config_skip_data()`, `config_get_level()`, and `config_get_zstd_params()`. `configs` is a NULL-terminated exported config list.

Control flow: The header itself has no executable flow. It shapes the runtime flow by allowing the harness to iterate `configs`, skip incompatible data, derive levels for simple APIs, and derive `ZSTD_parameters` for legacy advanced APIs.

State and persistence: All state described by this header is immutable configuration once compiled. It does not allocate or persist resources.

Dependencies and integration points: It uses `ZSTD_STATIC_LINKING_ONLY` before including `<zstd.h>` so internal/advanced parameter types are visible. It includes `data.h` because skip logic depends on dataset dictionary availability.

Risks and test signals: The API intentionally bridges several zstd API generations, so fields can be meaningful for one method and ignored by another. Adding new parameters requires checking both modern `ZSTD_CCtx_setParameter()` users and legacy `ZSTD_parameters` derivation. Correctness is signaled by consistent matrix rows across CLI and API methods and by intentional skips for incompatible configs.
