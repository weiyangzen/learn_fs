# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RunJar.java

## Purpose
`RunJar` unpacks and runs Hadoop job jars. It locates the target main class from a manifest or command line, prepares an isolated work directory, builds the classloader, invokes `main`, and cleans temporary files at shutdown.

## Important APIs, Types, And Functions
Important APIs are `main`, `run`, `unJar` overloads, deprecated `unJarAndSave`, `createWorkDirectory`, `directoryPermissions`, `userOnly`, and `createClassLoader`. Environment switches include `HADOOP_USE_CLIENT_CLASSLOADER`, `HADOOP_CLASSPATH`, `HADOOP_CLIENT_CLASSLOADER_SYSTEM_CLASSES`, and `HADOOP_CLIENT_SKIP_UNJAR`.

## Control Flow
`run` validates the jar file, reads `Main-Class` unless supplied, creates a secure temp directory, registers a shutdown hook to delete it, optionally unpacks the jar, creates either an `ApplicationClassLoader` or `URLClassLoader`, sets the context loader, loads the main class, shifts user args, and invokes `main`, unwrapping target exceptions. `unJar` checks canonical paths to prevent expanding entries outside the target directory.

## State And Persistence
Temporary unpacked files persist only until the shutdown hook deletes the work directory. Static configuration is read from environment variables at call time via methods.

## Dependencies And Integration Points
It integrates with `ShutdownHookManager`, `FileUtil`, Hadoop classloader isolation, commons `TeeInputStream`, jar APIs, and filesystem permissions.

## Risks
Jar execution is security-sensitive. Zip-slip protection and user-only temp permissions are essential. `System.exit` is used for usage/setup failures. Skipping unjar changes classpath assumptions around `classes/` and `lib/`. Shutdown cleanup may not run on hard kill.

## Test Signals
Tests should cover manifest and explicit main selection, argument shifting, zip-slip rejection, selective unpack regex, temp directory permissions on POSIX/ACL filesystems, client classloader env behavior, skip-unjar mode, and cleanup hook registration.
