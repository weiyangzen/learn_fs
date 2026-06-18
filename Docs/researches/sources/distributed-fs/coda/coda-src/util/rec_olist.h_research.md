# sources/distributed-fs/coda/coda-src/util/rec_olist.h

## Purpose
Declares the recoverable intrusive singly-linked list.

## Important APIs, Types, And Functions
`rec_olist`, `rec_olist_iterator`, and `rec_olink` mirror `olist` with RVM allocation and transaction annotations.

## Control Flow
Callers initialize or allocate lists in recoverable storage, insert and remove `rec_olink` objects inside transactions, and scan with an iterator.

## State And Persistence
The tail pointer, count, and link pointers are intended to be persistent. Object ownership remains external.

## Dependencies And Integration Points
Includes `olist.h` for conceptual parity and `rvmlib.h` for persistence.

## Risks
The iterator safety claim should be verified against implementation before deleting entries during traversal. No locks are provided.

## Test Signals
Compile persistent users and run recovery tests for singleton, head, tail, and clear paths.
