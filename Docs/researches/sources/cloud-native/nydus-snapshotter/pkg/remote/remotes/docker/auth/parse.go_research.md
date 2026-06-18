# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/parse.go

This file parses `WWW-Authenticate` headers into prioritized auth challenges. It defines bitmask-like authentication schemes for Basic, Digest, and Bearer, `Challenge`, and a sorter that orders higher scheme values first, making Bearer preferred over Digest and Basic.

`init` builds an octet classification table for RFC token and space parsing. `ParseAuthHeader` iterates canonical `WWW-Authenticate` headers, parses the auth scheme and parameters with `parseValueAndParams`, recognizes basic/digest/bearer schemes, appends challenges, and stable-sorts them by scheme priority. Parser helpers skip whitespace, parse tokens, and parse quoted values with backslash escaping.

There is no persistence. Integration points include token option generation and Docker registry authorizer behavior. Risks include a simplified parser that may not handle every legal auth header form, duplicate parameters overwriting earlier values, unclosed quoted strings returning empty values/rest, and unsupported schemes being ignored. Tests cover Bearer headers, empty quoted values, and fuzz arbitrary input for panics.
