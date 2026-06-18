# sources/distributed-fs/openafs/src/cmd/krb5_locl.h

Purpose: compatibility shim that lets Heimdal's `config_file.c` compile as OpenAFS `cmd` raw config parsing code without exposing a real Kerberos dependency.

Important APIs and types: maps `krb5_config_binding/section` to `cmd_config_binding/section`, defines minimal `krb5_context`, error, boolean, and deltat types, stubs Kerberos error-message helpers, and wraps Heimdal functions as `cmd_RawConfigParseFile*`, `cmd_RawConfigFileFree`, `cmd_RawConfigGetString/Bool/Int/List`. Under `EXPAND_PATH_HEADER`, it provides Windows path-expansion indirection and a dummy `SHGetFolderPath`.

Control flow and state: wrapper functions pass `NULL` Kerberos context into static Heimdal routines. `cmd_RawConfigGet*` use variadic path arguments to traverse config sections. No persistent state exists here beyond what Heimdal's parser allocates and returns.

Dependencies and integration: included only while compiling external Heimdal `config_file.c` in the cmd library. It depends on `cmd.h`, roken, and platform Windows headers when path expansion is built.

Risks and tests: the shim intentionally stubs Kerberos behavior, so future Heimdal changes may require new compatibility definitions. `krb5_abortx` aborts on fatal parser errors. Config behavior is indirectly tested through cmd option/config consumers.
