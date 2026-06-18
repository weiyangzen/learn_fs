# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/topology-broken-script.sh

Purpose: intentionally failing topology script fixture. It exists to verify that Hadoop topology resolution callers handle external scripts that fail.

Important APIs/functions: no functions are declared. The script exits with status `1` after comments explicitly warning not to fix it.

Control flow: execution immediately reaches `exit 1`, producing no topology output.

State and persistence behavior: no state, no output files, and no side effects.

Dependencies and integration points: used by HDFS/network topology tests that configure an external script-based rack resolver. It depends only on `/usr/bin/env bash`.

Risks: its failure is the contract. Any change that makes it succeed, print a rack, or depend on input would invalidate tests for broken topology handling.

Test signals: callers should observe non-zero exit status and exercise error/fallback paths without crashing or misclassifying nodes.
