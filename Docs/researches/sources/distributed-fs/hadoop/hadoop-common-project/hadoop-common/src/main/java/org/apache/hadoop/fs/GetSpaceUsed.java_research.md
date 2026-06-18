# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GetSpaceUsed.java

Purpose: `GetSpaceUsed` is a pluggable interface for reporting local directory space usage, with a builder that chooses DU or Windows implementation by platform/configuration.

Important APIs: `getUsed`, nested `Builder`, configuration/path/class/interval/jitter/initialUsed/constructor setters and getters, and `build`.

Control flow and state: `Builder` resolves defaults from `CommonConfigurationKeys`, selects `WindowsGetSpaceUsed` on Windows or `DU` elsewhere unless overridden, reflectively constructs a class with a `Builder` constructor, falls back to platform default on reflection failure, and calls `init` when the result is `CachingGetSpaceUsed`.

Dependencies and integration: used by disk usage monitors and local storage accounting. It depends on `Configuration`, `Shell`, `DU`, `WindowsGetSpaceUsed`, and `CachingGetSpaceUsed`.

Risks: reflection errors are logged and silently fall back, which can mask misconfiguration. `path` is not validated in the builder itself. Constructor caching through `cons` can interact badly if callers mutate `klass` afterward.

Test signals: default class selection per platform, configured class override, fallback on bad constructor, interval/jitter config defaults, initial used sentinel `-1`, and `CachingGetSpaceUsed.init` invocation.
