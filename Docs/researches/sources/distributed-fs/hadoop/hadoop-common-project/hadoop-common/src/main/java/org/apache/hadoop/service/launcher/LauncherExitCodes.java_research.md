# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LauncherExitCodes.java

Purpose: `LauncherExitCodes` defines the stable public exit-code vocabulary used by Hadoop service launchers and launchable services.

Important APIs and types: constants include success/failure basics (`EXIT_SUCCESS`, `EXIT_FAIL`), interrupt and shutdown codes, CLI/client errors in the 40s, service/server errors in the 50s, and service creation/lifecycle failures.

Control flow: `ServiceLauncher`, `ServiceLaunchException`, and `LaunchableService` implementations use these codes to convert Java exceptions and lifecycle outcomes into process exit statuses. Some values intentionally resemble HTTP status classes compressed into a byte-sized range.

State and persistence behavior: constant-only interface; no state, persistence, or validation logic.

Dependencies and integration points: public evolving API used by services, CLI callers, tests, and documentation. `ServiceLaunchException` implements this interface for convenient constant access.

Risks: codes are part of CLI compatibility. `EXIT_FAIL` is `-1`, which is meaningful inside Java but may be shell-normalized differently. Application-specific codes are expected at 60+, so new framework codes should avoid that range.

Test signals: verify launcher exception conversion chooses the documented codes, usage failures produce `EXIT_USAGE`, missing config files produce `EXIT_NOT_FOUND`, and service instantiation failures produce `EXIT_SERVICE_CREATION_FAILURE`.
