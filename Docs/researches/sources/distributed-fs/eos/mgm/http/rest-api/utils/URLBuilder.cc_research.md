## sources/distributed-fs/eos/mgm/http/rest-api/utils/URLBuilder.cc

Purpose: implements a fluent URL builder used for tape REST `.well-known` endpoint URLs.

Important APIs/types/functions: `getInstance`, `setHttpsProtocol`, `setHostname`, `setPort`, `add`, `build`, and `addSlashIfNecessary`.

Control flow: builder enforces call order through staged interfaces: protocol, hostname, port, then additional path pieces. `add` appends a slash only when the current URL does not end with `/` and next item does not start with `/`.

State and persistence: stores a mutable `mURL` string in the builder instance.

Dependencies and integration points: used by `TapeRestHandler::getAccessURLBuilder` and `.well-known` endpoint generation.

Risks and test signals: `addSlashIfNecessary` calls `mURL.back()` and assumes URL is non-empty; staged use satisfies this, but direct misuse after construction would be unsafe. Tests should cover leading/trailing slash combinations and port zero/unset config.
