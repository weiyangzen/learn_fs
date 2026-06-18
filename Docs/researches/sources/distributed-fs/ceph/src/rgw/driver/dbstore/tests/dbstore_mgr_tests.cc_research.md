# sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/dbstore_mgr_tests.cc

## Purpose
Unit tests `DBStoreManager` database-file naming, default handle creation, tenant lookup, tenant creation, and deletion behavior.

## APIs, Flow, And State
The fixture creates a standalone `CephContext`, sets `g_ceph_context`, moves into the system temp directory, creates `rgw_dbstore_tests`, and removes it on teardown. Helpers compute expected database full paths from `dbstore_db_dir`, `dbstore_db_name_prefix`, tenant, and `.db` suffix, and compute the `DB::getDBname()` tenant path without suffix.

Tests verify default DB file creation when `dbstore_db_dir` is set; prefix customization; the alternate manager constructor with log file/log level; `getDB(default_tenant, false)` and `getDB("", false)` return a DB named for the default tenant; missing tenant lookup returns `nullptr`; `getDB(new_tenant, true)` creates a new tenant handle; and `deleteDB(default_tenant)` removes the map entry so later lookup returns `nullptr`.

## Dependencies And Integration
Depends on `gtest`, `std::filesystem`, `common/ceph_context.h`, and `rgw/driver/dbstore/dbstore_mgr.h`. It exercises real database creation through `DBStoreManager`, so it depends on the dbstore backend compiled into the test target.

## Risks And Test Signals
These tests cover basic lifecycle and path naming but not object/user/bucket operations, concurrent `getDB()`, pointer deletion, repeated delete, or filesystem cleanup of database files. Because tests change current working directory and global Ceph context, isolation matters if more tests are added. The current signal is a good smoke test for manager construction and tenant mapping.
