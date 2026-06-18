# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PrintJarMainClass.java

## Purpose
`PrintJarMainClass` is a tiny private command-line utility that prints the `Main-Class` declared in a jar manifest. It is intended for scripts or launch plumbing that need to inspect jars without running them.

## Important APIs, Types, And Functions
The only API is `main(String[] args)`. It opens `args[0]` as a `JarFile`, obtains the manifest, reads the main attributes, and prints the normalized class name.

## Control Flow
The command tries to read the jar in a try-with-resources block. If a manifest and `Main-Class` exist, slashes are replaced with dots, the value is printed, and the method returns normally. Any `Throwable`, missing argument, unreadable jar, missing manifest, or absent attribute falls through to printing `UNKNOWN` and exiting with status `1`.

## State And Persistence
No mutable or persistent state is kept. The process writes one line to stdout and may terminate the JVM with a nonzero code.

## Dependencies And Integration Points
It depends on `java.util.jar.JarFile` and `Manifest`, plus Hadoop annotations. It pairs conceptually with `RunJar`, which uses the same manifest attribute to locate entry points.

## Risks
The broad `catch (Throwable)` hides malformed input details, including programming errors such as missing `args[0]`. Output goes to stdout even on failure, so callers must check exit status if `UNKNOWN` could also be meaningful.

## Test Signals
Tests should cover jars with slash and dotted `Main-Class` values, missing manifests, missing attributes, nonexistent files, empty argument arrays, and process exit code handling.
