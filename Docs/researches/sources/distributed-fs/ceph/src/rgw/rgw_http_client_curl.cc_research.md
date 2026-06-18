# sources/distributed-fs/ceph/src/rgw/rgw_http_client_curl.cc

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This file provides process-level curl/OpenSSL setup and cleanup. It installs legacy OpenSSL locking callbacks when needed, inspects frontend config to avoid double SSL initialization in old Beast/curl combinations, initializes curl once, starts the saved curl handle pool, and tears it down in cleanup. State is global and not persistent. Dependencies are libcurl, optional OpenSSL crypto APIs, frontend config, and `rgw_http_client.cc` handle-pool functions. Risks include once-only lifecycle semantics, legacy build-condition behavior, frontend-name-specific SSL detection, and cleanup ordering. Test signals include setup with/without frontend maps, repeated setup, cleanup after handle use, and old OpenSSL callback builds.
