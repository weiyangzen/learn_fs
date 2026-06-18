# sources/distributed-fs/openafs/src/util/errors.h

Purpose: Defines historical OpenAFS/VICE volume and server error codes used across volume, fileserver, and client-facing paths.

Important constants: Maps `VREADONLY` to `EROFS`; defines special volume errors starting at `VICE_SPECIAL_ERRORS` including `VSALVAGE`, `VNOVNODE`, `VNOVOL`, `VVOLEXISTS`, `VNOSERVICE`, `VOFFLINE`, `VONLINE`, `VDISKFULL`, `VOVERQUOTA`, `VBUSY`, `VMOVED`, `VIO`, `VSALVAGING`, `VRESTRICTED`, and negative `VRESTARTING`.

Control flow and state: Header-only constants, no runtime control flow or state. The numeric values are part of the protocol/behavioral contract between OpenAFS components.

Dependencies and integration: Relies on platform errno definitions such as `EROFS`. Included by components that need common error codes for volume operations and file-server responses.

Risks and test signals: Changing values would be wire/protocol incompatible. Some comments describe semantic distinctions, for example retryable busy/restarting versus offline/restricted states; callers must preserve these semantics. Tests are indirect through volume-server, cache-manager, and command behavior rather than this header.
