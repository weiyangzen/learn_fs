<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/build-and-install.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/build-and-install.sh

## Purpose
Builds the Hadoop 1 OrangeFS filesystem adapter with Maven and installs the resulting jar into the OrangeFS prefix.

## Important APIs, Types, And Functions
The script uses `mvn` with Java source/target 1.6, skips tests, runs `clean package`, and copies `target/orangefs-hadoop1-?.?.?.jar` to `${ORANGEFS_PREFIX}/lib/` with `sudo`.

## Control Flow
It enables shell tracing, changes to its own directory, then chains build and copy with `&&` so install runs only after a successful Maven package.

## State And Persistence
Creates Maven build artifacts under `target/` and installs a jar into the OrangeFS library directory.

## Dependencies And Integration Points
Depends on Maven, JDK compatible with source/target 1.6, sudo privileges, `ORANGEFS_PREFIX`, and `pom.xml` generated from `pom.xml.in`.

## Risks And Test Signals
Risks include unquoted `cd $(dirname $0)`, glob mismatch if version has more digits or multiple jars exist, skipped tests, and sudo prompting in automation. Test signals are successful Maven package, exactly one jar copied, and Hadoop classpath loading the installed adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/build-and-install.sh -->
