# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/contract/hdfs.xml

## Purpose
`hdfs.xml` is a filesystem contract-test resource declaring HDFS capabilities and expected behaviors for Hadoop contract tests.

## Important APIs, types, and functions
The file is an XML `configuration` resource with `property` entries. It enables root tests, sets random seek count, and declares HDFS support for case sensitivity, append, atomic directory delete, atomic rename, block locality, concat, seek, strict exceptions, Unix permissions, setTimes, getFileStatus, file references, content checks, unbuffer, hflush, and hsync. It declares rename return behavior for existing destination or missing source and states `metadata_updated_on_hsync=false`.

## Control flow
There is no executable control flow. Hadoop contract-test loaders read the resource as configuration and parameterize generic filesystem contract tests based on the property values.

## State and persistence behavior
The resource persists no runtime state. Its values influence which contract tests run and what behavior they expect from HDFS.

## Dependencies and integration points
It integrates HDFS with the Hadoop filesystem contract test framework. Property names are part of the contract-test schema used by generic FS tests.

## Risks and edge cases
Incorrect values can either skip meaningful HDFS coverage or cause generic contract tests to expect behavior HDFS does not provide. `metadata_updated_on_hsync=false` is a subtle semantic expectation that can affect durability/metadata tests.

## Test signals
The resource signals that HDFS should pass broad filesystem contract behavior around append, seek, rename, permissions, locality, flush/sync, and error strictness.
