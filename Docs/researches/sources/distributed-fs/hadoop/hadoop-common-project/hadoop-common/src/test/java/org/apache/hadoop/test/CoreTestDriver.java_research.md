# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/CoreTestDriver.java

Purpose: command-line driver registering selected core Hadoop tests with `ProgramDriver`.

Important APIs/types/functions: `ProgramDriver`, constructors, `run(String[])`, and `main`. Registered programs are `testsetfile`, `testarrayfile`, `testrpc`, and `testipc`.

Control flow: constructor creates or accepts a `ProgramDriver`, registers test classes and descriptions, and prints any registration throwable. `run` calls `pgd.run(argv)`, catches throwable, then exits the JVM with the resulting exit code. `main` constructs and runs the driver.

State and persistence behavior: stores one in-memory `ProgramDriver`. No file persistence, but it calls `System.exit`.

Dependencies and integration points: integrates with old Hadoop command-driver patterns and specific core test classes in `io` and `ipc`.

Risks and test signals: useful for manual/legacy test invocation but risky in embedded tests because it exits the JVM. Error handling prints stack traces rather than using structured logging.
