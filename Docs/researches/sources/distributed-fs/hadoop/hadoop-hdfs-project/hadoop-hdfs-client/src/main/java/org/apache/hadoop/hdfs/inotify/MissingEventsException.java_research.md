# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/MissingEventsException.java

## Purpose
`MissingEventsException` signals that an inotify client expected the next event batch to start at one transaction id but the NameNode returned a later transaction id, usually because intervening edits were removed during checkpointing.

## Important APIs, types, and functions
It extends `Exception`, stores `expectedTxid` and `actualTxid`, provides a no-arg constructor and a constructor for both ids, getters, and a detailed `toString`.

## Control flow
The exception carries txid metadata and formats a diagnostic string. No other behavior exists.

## State and persistence behavior
State is the two long txid values. There is no persistence.

## Dependencies and integration points
It is public/evolving in the HDFS inotify package and consumed by inotify stream clients as a signal that they cannot reconstruct a gap from available edit logs.

## Risks and test signals
Tests should verify txid preservation, default constructor values, serialization compatibility via `serialVersionUID`, and message clarity. Client code should handle this as a data-loss/gap condition rather than a transient retry alone.
