# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DoAsParam.java

## Purpose

`DoAsParam` represents the `doas` query parameter for WebHDFS proxy-user requests.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "doas"` and empty default, with constructor and `getName`.

## Control Flow

Null or empty-default values are stored as null. Non-empty proxy user names are passed through the domain without a regex in this class.

## State And Persistence

Only the proxy user string is stored.

## Dependencies And Integration Points

`WebHdfsFileSystem.getAuthParameters` emits this when current UGI has a real user.

## Risks

Validation is delegated elsewhere, so malformed names reach server-side checks. User identity values in URLs can be logged.

## Test Signals

Tests should cover proxy-user auth parameter construction, omission for non-proxy users, empty/null values, and URL encoding.
