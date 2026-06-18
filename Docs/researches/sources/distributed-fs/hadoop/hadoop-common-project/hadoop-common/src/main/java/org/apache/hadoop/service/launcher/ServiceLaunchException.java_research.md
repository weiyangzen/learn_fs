# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceLaunchException.java

Purpose: `ServiceLaunchException` is the launcher-specific `ExitUtil.ExitException` subclass that carries a process exit code plus an optional formatted message and cause.

Important APIs and types: constructors accept `(exitCode, Throwable)`, `(exitCode, String)`, `(exitCode, format, args...)`, and `(exitCode, cause, format, args...)`. It implements `ExitCodeProvider` and `LauncherExitCodes`.

Control flow: `ServiceLauncher` throws or returns this exception for argument, service creation, lifecycle, and generic execution failures. Formatted constructors use `String.format(Locale.ENGLISH, ...)`; the varargs constructor also treats a trailing `Throwable` as a cause.

State and persistence behavior: stores only the inherited exit code, message, and cause. It has no persistence behavior.

Dependencies and integration points: integrates with `ExitUtil.terminate`, `ExitCodeProvider`, and the launcher exception-conversion path.

Risks: the varargs constructor includes the trailing throwable in format substitution while also installing it as cause, so format strings must account for it. Locale is fixed to English for reproducibility.

Test signals: cover exit-code retention, cause initialization in both cause-taking paths, formatted messages under non-English default locales, and launcher pass-through of existing `ExitException` instances.
