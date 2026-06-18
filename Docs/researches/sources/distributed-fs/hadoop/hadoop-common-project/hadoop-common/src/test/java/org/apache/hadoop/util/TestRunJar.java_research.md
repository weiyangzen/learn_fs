# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestRunJar.java

Purpose: tests `RunJar`, Hadoop's jar unpacking and application launching utility, including extraction filtering, timestamp preservation, client classloader behavior, and path traversal defense.

Important APIs and types: `RunJar.unJar`, `unJarAndSave`, `createWorkDirectory`, `run`, `MATCH_ANY`, `ApplicationClassLoader`, `JarFinder.makeClassLoaderTestJar`, Mockito spy/stubbing, `FileUtil`, and Java jar streams.

Control flow: setup creates a jar with two entries and fixed modification times. Tests unjar all entries, unjar by regex, generate a larger jar and verify `unJarAndSave` preserves saved jar length plus extracted file sizes, assert extracted modification times equal entry times, create/delete a work directory, run a generated classloader test jar with client classloader enabled, verify optional skip-unjar avoids unpacking, and create a malicious `../outside.path` entry that must fail for both file and stream unjar APIs.

State and persistence: extensive temporary filesystem and jar state under a per-test root, cleaned in `tearDown`.

Dependencies and integration points: covers job jar handling, classloader isolation, and archive security for Hadoop launch paths.

Risks: zip-slip path traversal, lost timestamps, partial extraction, classloader parent/child mistakes, and temporary directory leaks. Test signals are file existence/absence, size/timestamp equality, Mockito call counts, and exception message checks.
