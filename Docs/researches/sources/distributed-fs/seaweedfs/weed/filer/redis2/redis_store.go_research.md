# sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_store.go

## Purpose

`redis2/redis_store.go` registers the second-generation single-node Redis store with username, key-prefix, super-large-directory, and optional mTLS support. It was read as a complete 81-line file.

## Important APIs, Types, and Functions

`Redis2Store` embeds `UniversalRedis2Store`. `Initialize` reads address, username/password, database, key prefix, super-large directories, and mTLS certificate paths. `initialize` creates `redis.Options`, optionally builds `tls.Config`, then assigns the client and directory settings.

## Control Flow

When mTLS is enabled, the file loads client cert/key, reads CA PEM, parses host name for `ServerName`, and installs TLS 1.2+ config before creating the Redis client.

## State and Persistence Behavior

The file only owns connection and namespace setup; entry persistence is in the v2 universal store.

## Dependencies and Integration Points

Depends on `crypto/tls`, `crypto/x509`, `os.ReadFile`, `net.SplitHostPort`, `glog.Fatalf`, go-redis, and SeaweedFS config.

## Risks and Edge Cases

mTLS failures call `glog.Fatalf`, terminating the process instead of returning errors. Invalid host:port also exits. No connection ping is performed.

## Test Signals

Needed tests include mTLS config error paths, key-prefix isolation, username auth, and super-large-directory listing semantics.
