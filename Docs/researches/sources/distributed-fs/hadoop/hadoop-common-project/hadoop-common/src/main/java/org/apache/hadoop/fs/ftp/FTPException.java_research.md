# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPException.java

## Purpose
Runtime exception for FTP filesystem failures that occur in contexts not declaring checked IOExceptions.

## Important APIs, Types, and Functions
Constructors accept message, cause, or message plus cause.

## Control Flow
No flow; wraps FTP client state/cleanup failures.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Used by FTPFileSystem and FTPInputStream for connection and transfer-completion errors.

## Risks and Test Signals
Tests should verify close/home-directory failure paths preserve causes and messages.
