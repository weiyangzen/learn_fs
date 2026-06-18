<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/shellprofile.d/hadoop-hdfs.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/shellprofile.d/hadoop-hdfs.sh

## Purpose
This shell profile registers the HDFS component with Hadoop's shell launcher framework and contributes HDFS jars, resources, webapps, and optional build output to the process classpath.

## Important APIs, Types, And Functions
- Calls `hadoop_add_profile hdfs` when sourced, making the profile available to Hadoop shell initialization.
- Defines `_hdfs_hadoop_classpath`, the profile hook that appends HDFS-specific classpath entries.
- Uses launcher helper APIs `hadoop_add_classpath` and `hadoop_add_profile`.
- Reads launcher environment variables: `HADOOP_ENABLE_BUILD_PATHS`, `HADOOP_HDFS_HOME`, `HDFS_DIR`, and `HDFS_LIB_JARS_DIR`.

## Control Flow
When the profile is sourced, it immediately registers the `hdfs` profile. Later, when Hadoop shell code builds the classpath for this profile, `_hdfs_hadoop_classpath` runs. If `HADOOP_ENABLE_BUILD_PATHS` is non-empty, it adds `${HADOOP_HDFS_HOME}/hadoop-hdfs/target/classes` for developer builds. If `${HADOOP_HDFS_HOME}/${HDFS_DIR}/webapps` exists, it adds `${HADOOP_HDFS_HOME}/${HDFS_DIR}` so webapp resources are visible. It always adds globbed jar paths from the HDFS lib jar directory and the main HDFS directory.

## State And Persistence
The script has no persistent state. Its stateful effect is process-local mutation of the Hadoop classpath assembled by the parent shell launcher. Because it is sourced, function definitions and profile registration live in the caller's shell process.

## Dependencies And Integration Points
The file depends on the Hadoop shell function library already defining `hadoop_add_profile` and `hadoop_add_classpath`. It integrates with Hadoop distribution layout conventions where HDFS jars live under `${HADOOP_HDFS_HOME}/${HDFS_DIR}` and dependency jars under `${HADOOP_HDFS_HOME}/${HDFS_LIB_JARS_DIR}`. It also supports in-tree Maven builds through the `target/classes` path.

## Risks And Edge Cases
- Missing or wrong `HADOOP_HDFS_HOME`, `HDFS_DIR`, or `HDFS_LIB_JARS_DIR` values produce incomplete classpaths.
- The webapp classpath addition is conditional on the `webapps` directory; packaging changes that relocate webapps can break NameNode/DataNode web UI resource discovery.
- Build-path mode may accidentally prefer un-packaged classes over jars if enabled in production-like shells.
- Glob paths are intentionally appended as quoted prefix plus literal `/*`; downstream helper behavior must preserve expansion semantics expected by Hadoop launch scripts.

## Test Signals
Good signals include running HDFS shell commands from an installed distribution, checking `hadoop classpath`/HDFS daemon classpaths include HDFS jars and webapps, developer-build command tests with `HADOOP_ENABLE_BUILD_PATHS=1`, and packaging tests that verify the profile is sourced during daemon/client startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/shellprofile.d/hadoop-hdfs.sh -->
