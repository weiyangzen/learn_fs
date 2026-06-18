<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/taskcontroller.cfg -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/taskcontroller.cfg

## Purpose

This executor/task-controller configuration is a placeholder for privileged Hadoop task execution settings in the example cluster.

## Important APIs, Types, and Functions

The active keys describe local directories, log directories, task kill grace periods, Linux container-executor group, banned users, minimum uid, and allowed system users depending on Hadoop generation.

Active directives observed:

- `mapred.local.dir=#configured value of mapred.local.dir. It can be a list of comma separated paths.`
- `hadoop.log.dir=#configured value of hadoop.log.dir.`
- `mapred.tasktracker.tasks.sleeptime-before-sigkill=#sleep time before sig kill is to be sent to process group after sigterm is sent. Should be in seconds`
- `mapreduce.tasktracker.group=#configured value of mapreduce.tasktracker.group.`

## Control Flow

Hadoop task controller or NodeManager container-executor reads the file when secure/local container launch support is enabled. The example leaves values as comments/placeholders, so normal non-secure examples do not depend on it.

## State, Persistence, and Concurrency

No data is persisted by this file. It gates process launch permissions when enabled.

## Dependencies and Integration Points

It depends on Hadoop native/container-executor installation, filesystem permissions, and matching groups/users on all worker nodes.

## Risks and Test Signals

Leaving placeholders in a secure deployment can block task launch or accidentally permit/deny the wrong users. Test by running a small YARN/MapReduce job under the intended user and checking NodeManager/task-controller logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/taskcontroller.cfg -->
