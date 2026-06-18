# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/ExcludePrivateAnnotationsStandardDoclet.java

Purpose: JDK 17 `Doclet` implementation that wraps `StandardDoclet` and excludes Hadoop Private/LimitedPrivate APIs, with stability option support.

Important APIs, types, and functions: static legacy methods mirror old doclet entry points: `languageVersion()`, `start()`, `optionLength()`, and `validOptions()`. Instance methods implement `Doclet`: `init()`, `getName()`, `getSupportedOptions()`, `getSupportedSourceVersion()`, and `run()`. `getSupportedOptions()` adds `-unstable` and `-evolving` options to the delegate's options.

Control flow: javadoc constructs the doclet, calls `init()`, reads supported options, processes stability flags, then `run()` applies `StabilityOptions` and should run the delegate on a filtered environment. The static `start()` path prints the doclet name and runs `StandardDoclet` directly when elements are present.

State and persistence: instance state holds delegate, reporter, and locale; global stability state lives in `StabilityOptions` and `RootDocProcessor`.

Dependencies and integration points: integrates with JDK `StandardDoclet`, Hadoop annotation filtering, and the compiler POM's `jdk.javadoc` export because filtering uses `HadoopDocEnvImpl`.

Risks and test signals: `run()` calls `RootDocProcessor.process(environment)` but ignores the returned filtered environment and passes the original `environment` to `delegate.run()`, which appears to bypass filtering in the instance doclet path. The custom options omit `-stable` despite `StabilityOptions` supporting it. Test signals should verify generated docs actually exclude Private/LimitedPrivate elements for both legacy static and JDK 17 instance entry points.
