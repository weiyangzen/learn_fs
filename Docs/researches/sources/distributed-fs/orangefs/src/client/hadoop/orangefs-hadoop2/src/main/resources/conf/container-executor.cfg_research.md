<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/container-executor.cfg -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/container-executor.cfg

## Purpose

This executor/task-controller configuration is a placeholder for privileged Hadoop task execution settings in the example cluster.

## Important APIs, Types, and Functions

The active keys describe local directories, log directories, task kill grace periods, Linux container-executor group, banned users, minimum uid, and allowed system users depending on Hadoop generation.

Active directives observed:

- `yarn.nodemanager.linux-container-executor.group=#configured value of yarn.nodemanager.linux-container-executor.group`
- `banned.users=#comma separated list of users who can not run applications`
- `min.user.id=1000#Prevent other super-users`
- `allowed.system.users=##comma separated list of system users who CAN run applications`

## Control Flow

Hadoop task controller or NodeManager container-executor reads the file when secure/local container launch support is enabled. The example leaves values as comments/placeholders, so normal non-secure examples do not depend on it.

## State, Persistence, and Concurrency

No data is persisted by this file. It gates process launch permissions when enabled.

## Dependencies and Integration Points

It depends on Hadoop native/container-executor installation, filesystem permissions, and matching groups/users on all worker nodes.

## Risks and Test Signals

Leaving placeholders in a secure deployment can block task launch or accidentally permit/deny the wrong users. Test by running a small YARN/MapReduce job under the intended user and checking NodeManager/task-controller logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/container-executor.cfg -->
