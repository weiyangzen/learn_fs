# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/VersionInfo.java

Purpose: `VersionInfo` loads build metadata from `<component>-version-info.properties` and exposes the Hadoop Common version, revision, branch, build date/user/url, source checksum, protobuf compiler version, and compile platform.

Important APIs/types/functions: constructor `VersionInfo(String component)` loads a properties resource. Protected `_get*` methods read properties with `"Unknown"` defaults. Static `COMMON_VERSION_INFO` backs public static getters such as `getVersion`, `getRevision`, `getBuildVersion`, and `getCompilePlatform`. `main` prints version information and the containing jar.

Control flow: construction opens the resource through `ThreadUtil.getResourceAsStream`, loads `Properties`, logs a warning on `IOException`, and closes via `IOUtils.closeStream`. Public static getters delegate to the common singleton.

State and persistence behavior: build metadata is cached in a `Properties` instance for the life of the class. If loading fails, the cache remains mostly empty and getters return `"Unknown"`.

Dependencies and integration points: depends on `ThreadUtil`, `IOUtils`, SLF4J, and `ClassUtil`. `StringUtils.createStartupShutdownMessage` includes `VersionInfo` data in daemon startup logs.

Risks: missing or malformed resource files degrade silently to `"Unknown"` values after logging. The singleton is initialized at class load, so classpath issues are fixed for the process. `main` writes build details to stdout, which is intended for CLI use.

Test signals: tests should provide classpath resources, verify default values when absent, and assert printed output contains version and jar location.
