# sources/distributed-fs/ceph/src/rgw/rgw_rest_admin.h

## Purpose

Declares the base REST manager class for admin resources.

## Important APIs, Types, and Functions

`RGWRESTMgr_Admin` derives from `RGWRESTMgr` and provides default constructor/destructor only.

## Control Flow and Data Flow

The class serves as a type marker/extension point for admin resource manager registration. Actual routing behavior is inherited from `RGWRESTMgr`.

## State and Persistence Behavior

No additional state or persistence behavior beyond `RGWRESTMgr`.

## Dependencies and Integration Points

Depends on `rgw/rgw_rest.h`. Integrated with admin API setup that registers sub-managers for users, buckets, accounts, metadata, and related admin resources.

## Risks and Edge Cases

Because it adds no overrides, all behavior depends on resources registered on the inherited manager. Missing subresource registration will fall back to default manager behavior.

## Test Signals

Compile coverage, admin manager construction/destruction, resource registration through inherited APIs, and default routing behavior with unknown admin paths.
