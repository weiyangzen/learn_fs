# sources/distributed-fs/beegfs/client_module/source/fault-inject/fault-inject.h

## Purpose
Declares BeeGFS fault-injection hooks with no-op fallbacks for non-debug or non-fault-injection builds.

## Important APIs and types
When enabled, includes kernel fault injection, requires debugfs and fault-injection debugfs configs, declares `fault_attr` externs, defines `BEEGFS_SHOULD_FAIL(name, size)` as `should_fail`, and exports init/release. When disabled, `BEEGFS_SHOULD_FAIL` is constant false and init/release are inline no-ops.

## State, dependencies, integration
The header is included by code paths that need conditional failure injection without carrying config-specific preprocessor logic at each call site.

## Risks and test signals
Builds with `BEEGFS_DEBUG` and fault injection but missing debugfs configs intentionally fail preprocessing. Tests should compile both enabled and disabled configurations and validate call sites remain type-correct when the macro collapses to false.
