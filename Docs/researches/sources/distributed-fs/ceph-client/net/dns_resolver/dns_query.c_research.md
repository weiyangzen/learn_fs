# sources/distributed-fs/ceph-client/net/dns_resolver/dns_query.c

## Purpose
This file implements `dns_query()`, the kernel API that performs DNS resolution by requesting a `dns_resolver` key, causing a userspace upcall when needed, and returning the cached payload to callers.

## Important APIs, Types, And Functions
`dns_query()` is exported. Its inputs are network namespace, optional query type, name and length, request-key options, optional result/expiry outputs, and an `invalidate` flag. It builds key descriptions of the form `[type:]name`, calls `request_key_net()` with `key_type_dns_resolver`, reads `struct user_key_payload`, and optionally invalidates the key after use.

## Control Flow
The function rejects NULL/empty names, empty query types, and names shorter than 3 or longer than 255 bytes. It allocates a description buffer, appends `type:` when present, appends the name, and uses an empty options string if options are NULL. The request is performed under `dns_resolver_cache` credentials through `scoped_with_creds()` to prevent unprivileged users from steering lookups with preinstalled keys.

After `request_key_net()` returns a key, the code takes `rkey->sem` for reading, allows root invalidation/viewing, validates the key, returns a stored DNS error if present, copies payload data with `kmemdup_nul()` when requested, optionally returns key expiry, unlocks, optionally invalidates, and drops the key reference.

## State And Persistence
The function itself keeps no persistent state. Results live in the DNS resolver key cache. Callers own the duplicated `_result` buffer and must free it. When `invalidate` is true, the key is invalidated after the read, forcing a future upcall.

## Dependencies And Integration Points
This depends on `dns_key.c` registering `key_type_dns_resolver`, the keyring/request-key infrastructure, userspace request-key configuration, and network namespaces through `request_key_net()`. It is consumed by kernel filesystem/network clients that need DNS lookups, such as AFS and CIFS.

## Risks And Edge Cases
The name length lower bound of 3 rejects very short names even if a resolver could handle them. If `_result` is NULL, the caller only receives length/expiry/error. The function mutates key flags/permissions while holding the key semaphore, which is expected here but relevant to security review. Userspace helper failures surface as request-key or stored DNS error codes.

## Test Signals
Tests should cover validation failures, successful A/host lookups, typed lookups, namespace-specific upcalls, `_result == NULL`, expiry output, invalidation behavior, DNS error propagation, and memory ownership of the returned buffer.
