# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/options.h

Purpose: `options.h` defines translator volume option metadata, validation categories, and macros that initialize/reconfigure typed option values from dictionaries.

Important APIs and types: `volume_option_type_t` covers string, integer, size, percent, boolean, xlator, path, time, double, address/list, priority, size-list, and auth address options. `volume_option_t` stores aliases, type, validation range, allowed values, defaults, description, op-version/deprecation arrays, flags, tags, setkey, level, and category. APIs include `xlator_options_validate`, `xlator_option_validate`, address-list validation, option lookup, and generated `xlator_option_init_*`/`xlator_option_reconf_*` functions.

Control flow and state: `DEFINE_INIT_OPT` fetches metadata from the translator, chooses explicitly set value over default, converts with a provided converter, then validates. `DEFINE_RECONF_OPT` repeats this flow for reconfiguration using `dict_get_strn`. `GF_OPTION_INIT` and `GF_OPTION_RECONF` jump to caller error labels on failure.

Dependencies and integration: depends on `xlator.h`, dictionaries, logging, and message IDs. Graph activation calls option validation before translator init. GD2 compatibility comments make `volume_option_t` layout ABI-sensitive.

Risks: macros hide gotos and require converter signatures to match. Struct member ordering is externally constrained. Missing defaults produce zero values without validation. Reconfiguration uses string length from `strlen(key)` and relies on stable dictionary ownership.

Test signals: validate each option type, min/max/range flags, alias matching, default precedence, bad conversion, op-version/deprecation handling, unknown option logging, and GD2 layout compatibility.
