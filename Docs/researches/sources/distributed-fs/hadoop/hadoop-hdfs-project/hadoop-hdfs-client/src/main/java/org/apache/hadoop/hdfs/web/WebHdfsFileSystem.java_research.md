# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/WebHdfsFileSystem.java

## Purpose

`WebHdfsFileSystem` implements Hadoop `FileSystem` over the WebHDFS REST API. It maps filesystem methods to HTTP operations, manages authentication and delegation tokens, handles HA failover/retry, parses JSON responses, and provides streaming reads/writes over redirected NameNode/DataNode connections.

## Important APIs, Types, And Functions

Important public methods include initialization, status/list/open/create/append/delete/rename/mkdirs, xattr/ACL/snapshot/storage-policy/EC/quota/checksum/trash/block-location APIs, delegation-token operations, KMS integration, capabilities, and multipart uploader creation. Important nested runners are `AbstractRunner`, `AbstractFsPathRunner`, `FsPathResponseRunner`, `FsPathOutputStreamRunner`, `URLRunner`, `WebHdfsInputStream`, and `ReadRunner`.

## Control Flow

`initialize` configures user/ACL patterns, connection factory, HA/non-HA retry policy, token service, working directory, security fallback rules, CSRF headers, and statistics. URLs are built from operation parameters plus either delegation tokens or user/doAs parameters. `AbstractRunner` executes calls inside UGI `doAs`, resolves redirects for DataNode operations, validates response codes, refreshes expired tokens, excludes failed datanodes, and applies retry/failover policy. Filesystem methods wrap this pattern with operation-specific params and JSON decoders.

## State And Persistence

State includes UGI, URI, current delegation token, token service, NameNode addresses/current index, retry policy, working/home directories, CSRF settings, connection factory, server-compatibility flags, and read-stream connection state. No client-side persistence exists. Closing cancels owned delegation tokens and destroys the connection factory.

## Dependencies And Integration Points

It integrates with Hadoop `FileSystem`, WebHDFS resource params/op enums, `JsonUtilClient`, UGI/SPNEGO/delegation tokens, HA utilities, retry policies, KMS/key providers, storage statistics, HTTP headers, SSL/OAuth factories, and HDFS protocol models.

## Risks

This is high-blast-radius code. Risks include auth fallback mistakes between secure and insecure clusters, token refresh during retries, HA failover state races, redirect handling for create/append/open/checksum, CSRF header method filtering, JSON schema compatibility, old server fallback for block locations, and stream reconnection after seek/read failures. `ReadRunner.closeInputStream` nulls `in` before closing it, so any intended stream close relies on connection close behavior and merits focused review.

## Test Signals

Coverage should include MiniDFS/WebHDFS secure and insecure modes, HA failover, token acquisition/renew/cancel/expiry replacement, create/append two-step redirects, open/seek/read retry behavior, encrypted file reads, CSRF configuration, all REST operation mappings, old/new block location ops, KMS token issuer behavior, and response validation/error unwrapping.
