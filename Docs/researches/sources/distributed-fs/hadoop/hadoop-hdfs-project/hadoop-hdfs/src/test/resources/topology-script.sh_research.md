# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/topology-script.sh

Purpose: simple rack topology script fixture. It maps an input hostname or node name containing hyphen-delimited fields into a rack path.

Important APIs/functions: single pipeline `echo $1 | awk -F'-' '{printf("/rackID-%s",$2)}'`. It reads only the first argument and uses the second hyphen-separated field as the rack suffix.

Control flow: shell expands `$1`, `awk` splits on `-`, and the script prints `/rackID-<field2>` without a trailing newline from `printf`.

State and persistence behavior: no persistent state and no side effects.

Dependencies and integration points: used by topology resolver tests. Depends on Bash and `awk`, and on test node names having a meaningful second hyphen-delimited field.

Risks: unquoted `$1` permits word splitting and glob expansion, which is acceptable for controlled fixtures but unsafe for general input. Inputs without a second field produce `/rackID-`, so tests must use well-formed node names.

Test signals: resolver tests can assert that script-based topology resolution converts node names into deterministic rack strings.
