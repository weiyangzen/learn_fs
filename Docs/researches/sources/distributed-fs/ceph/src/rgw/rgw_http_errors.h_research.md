# sources/distributed-fs/ceph/src/rgw/rgw_http_errors.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header declares HTTP error maps for RGW protocols and inline `rgw_http_error_to_errno()`. It maps 2xx to success, common 304/400/401/403/404/405/409/503 statuses to RGW/Linux-style negative errors, and all other statuses to `-ERR_INTERNAL_ERROR`. It integrates with HTTP request completion and higher-level S3/Swift/STS/IAM error handling. Risks are loss of specificity for redirects and uncommon status codes. Tests should assert exact mappings and callers' ability to inspect raw HTTP status separately.
