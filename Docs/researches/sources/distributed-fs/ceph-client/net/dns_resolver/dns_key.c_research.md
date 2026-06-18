# sources/distributed-fs/ceph-client/net/dns_resolver/dns_key.c

## Purpose
This file defines the `dns_resolver` key type used to cache DNS lookup results supplied by userspace request-key upcalls. It validates payload formats, stores successful answers or DNS error codes in key payload slots, implements key matching semantics for DNS descriptions, exposes payloads through key read/describe methods, and initializes credentials used by DNS upcalls.

## Important APIs, Types, And Functions
Key payload words are indexed by `dns_key_data` and `dns_key_error` from `internal.h`. `dns_resolver_preparse()` validates instantiation data and fills `struct key_preparsed_payload`. `dns_resolver_free_preparse()` frees preparsed payloads. `dns_resolver_cmp()` implements case-insensitive matching and ignores a trailing dot in either key description. `dns_resolver_read()` copies cached result bytes to userspace. The file defines and registers `struct key_type key_type_dns_resolver`, and module init/exit functions register/unregister the key type.

It also exports module parameter `dns_resolver_debug` and holds `const struct cred *dns_resolver_cache`, the special credential set used by `dns_query()` to avoid malicious preinstalled redirections.

## Control Flow
For normal hostname results, `dns_resolver_preparse()` requires NUL-terminated data, strips the final NUL from the stored result length, then scans `#`-separated options. The only recognized option is `dnserror=<1..511>`, which stores an error pointer in the error payload slot and intentionally avoids caching a data payload. Unknown or malformed options reject the key with `-EINVAL`.

For non-string server-list payloads, the data must begin with zero and match the version-1 packed server-list header from the DNS resolver UAPI. The content type must be `DNS_PAYLOAD_IS_SERVER_LIST`, the version must be 1, and bad/non-good lookup status gets a very short default expiry when userspace did not provide one. Valid data is copied into a flex-array `struct user_key_payload`.

Key matching compares exact descriptions first, then compares both descriptions case-insensitively after ignoring one trailing dot. Read path validates the key, returns the payload length for size queries, or copies payload data into the caller's buffer.

## State And Persistence
Results are stored in the kernel key retention service. Key payload data persists until key expiry, invalidation, revocation, garbage collection, or module/key type teardown. Error-only keys store an encoded negative errno in `payload.data[dns_key_error]` and no result payload. `dns_resolver_cache` credentials persist while the module is loaded.

## Dependencies And Integration Points
This integrates with `<keys/dns_resolver-type.h>`, `<keys/user-type.h>`, keyctl/request-key infrastructure, DNS resolver UAPI structures, and `dns_query.c`. It depends on userspace instantiating keys through request-key helpers with the expected string or server-list format.

## Risks And Edge Cases
The option parser rejects any option except `dnserror`, so future options require code changes. Error numbers outside 1..511 are rejected. Server-list payload validation checks header content/version but does not fully walk every embedded server/address record here; malformed lengths beyond the basic size can still be a consumer-side risk. Normal result data containing `#` is treated as option-delimited, not literal data. Short expiry for failed server-list lookups intentionally limits negative caching.

## Test Signals
Useful tests instantiate keys with simple results, trailing-dot descriptions, mixed-case lookups, `dnserror` payloads, malformed options, missing NUL termination, valid and invalid server-list headers, and read buffers shorter/longer than the payload. Request-key integration tests should verify `dns_query()` observes error-only and data payloads correctly.
