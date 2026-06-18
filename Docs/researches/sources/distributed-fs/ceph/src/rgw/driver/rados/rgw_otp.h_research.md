# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_otp.h

## Purpose
Declares the RADOS OTP metadata integration API. It provides a stable way to derive OTP metadata keys and to construct the metadata handler used by the RGW metadata manager.

## Important APIs
`rgwrados::otp::get_meta_key(const rgw_user&)` returns the metadata key for a user's OTP data. `create_metadata_handler()` accepts system object, cls, mdlog, and zone parameter services and returns a `std::unique_ptr<RGWMetadataHandler>`.

## State, Dependencies, And Integration
The header stores no state. It depends only on forward declarations for RGW services and user/zone types, making it a small factory interface. Concrete persistence and listing behavior live in `rgw_otp.cc`. Tests should verify the key contract and that the factory registers a handler whose type is `"otp"`.
