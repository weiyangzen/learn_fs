# sources/distributed-fs/openafs/src/helper-splint.sh.in

Purpose: template shell helper for invoking `splint` with the OpenAFS common configuration and optional local overrides.

Important behavior: configure substitutes `@TOP_SRCDIR@` and `@HELPER_SPLINTCFG@`. The script initializes `cfargs` with the common helper config. If `splint-append.cfg` exists, it appends that config after the common one; otherwise if `splint.cfg` exists, it replaces the common config; otherwise it uses only the common config. It then execs `splint $cfargs -bad-flag "$@"`.

Control flow and state: no persistent state. It performs read checks in the current directory, so behavior depends on invocation working directory.

Dependencies and integration: used by developer/static-analysis workflows rather than runtime OpenAFS code. It depends on `splint` being installed and on configure-generated paths.

Risks: unquoted `$cfargs` intentionally expands into arguments but can be fragile if configured paths contain spaces. `TOP_SRCDIR` is assigned but unused. Test signals should run the helper in directories with no local config, with `splint.cfg`, and with `splint-append.cfg` to confirm intended precedence and argument construction.
