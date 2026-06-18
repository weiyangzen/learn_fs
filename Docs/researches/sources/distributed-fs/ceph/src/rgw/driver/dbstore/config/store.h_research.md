# sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/store.h

## Purpose
Declares the dbstore config-store factory API.

## APIs, Flow, And State
`rgw::dbstore::create_config_store(const DoutPrefixProvider*, const std::string&)` returns a `std::unique_ptr<sal::ConfigStore>`. The header contains no state and deliberately hides concrete backend classes from users.

## Dependencies And Integration
Includes `rgw_sal_config.h` for `sal::ConfigStore` and forward uses `DoutPrefixProvider`. Implemented by `store.cc`; callers include this when constructing dbstore config storage from a URI.

## Risks And Test Signals
The API does not advertise supported URI schemes, so runtime failure is the discovery mechanism. Compile-time signal is minimal; runtime tests should assert expected backend selection and exception behavior.
