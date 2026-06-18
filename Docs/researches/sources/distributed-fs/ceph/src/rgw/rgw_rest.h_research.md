# sources/distributed-fs/ceph/src/rgw/rgw_rest.h

## Purpose

Declares the common REST interface, object-store operation subclasses, REST routing managers, request/response helpers, and input parsing utilities used across RGW REST protocols.

## Important APIs, Types, and Functions

Exports initialization/flush functions, `rgw_sanitized_hdrval()`, JSON input helper, `RESTArgs`, `RGWRESTFlusher`, many `RGW*ObjStore` operation subclasses, `RGWRESTOp`, `RGWHandler_REST`, `RGWRESTMgr`, `RGWREST`, content-length constants, header/body dump helpers, `parse_content_length()`, `compute_domain_uri()`, and `rgw_rest_transform_s3_vhost_style()`.

## Control Flow and Data Flow

The header defines the reusable shape of REST operations: handlers allocate per-method ops, ops parse params and send responses through `RGWRESTFlusher`, managers route URI prefixes, and `RGWREST` ties manager resolution to frontend IO. Inline helpers sanitize metadata header values, parse content length, and derive request domain URI from request state/env.

## State and Persistence Behavior

Most declarations operate on per-request `req_state`. `rgw_to_http_attrs` is global mapping state initialized at runtime. Operation subclasses hold parsed request payloads or flags but persistence is handled in base operation implementations and storage drivers.

## Dependencies and Integration Points

Depends on RGW operation hierarchy, formatters, client IO, Lua background declarations, Ceph JSON/string helpers, and Boost flat sets. It is included by S3, Swift, admin, account, bucket logging, and other REST dialect handlers.

## Risks and Edge Cases

The many thin `ObjStore` subclasses rely on base-class behavior; changing base op contracts can affect many REST paths. `RGWGetObjAttrs_ObjStore::get_params()` remains pure virtual despite default response methods. `dump_header_quoted()` declares an unused template parameter pack, which is harmless but unusual. `parse_content_length()` treats empty content length as zero and invalid strings as -1.

## Test Signals

Build coverage for all subclasses, formatter allocation/reallocation, header sanitization with trailing NULs and embedded NULs, JSON input parse failures, manager registration/routing, REST handler ownership, and protocol-specific operation factories using these declarations.
