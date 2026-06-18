# sources/control-plane/mayastor/test/python/tests/cli_controller/test_cli_controller.py

## Purpose
Validates Mayastor CLI controller listing and statistics for nexus child controllers.

## Important APIs, Types, And Functions
Fixtures create replicas and a published nexus. Helpers `assure_controllers` and `ctrl_name_from_uri` map child URIs to expected controller names. Tests `test_controller_list` and `test_controller_stats` use `get_msclient().with_json_output()` and SPDK fio traffic.

## Control Flow
The tests create two remote replicas and a nexus, query controller lists from replica and nexus nodes, remove/add a child, then run SPDK fio and assert stats counters and byte counts are present for both controllers.

## State And Persistence
State includes pools, replicas, nexus, child controllers, CLI output, and fio-generated IO. Fixture teardown destroys pools and nexus.

## Dependencies And Integration Points
Depends on common fixtures, `MayastorClient`, `FioSpdk`, v0 gRPC, JSON CLI output, and SPDK fio.

## Risks
Controller naming is parsed from URI path components and can break with URI format changes. Stats expectations depend on fio completing and controller counters being updated before the next CLI query.

## Test Signals
Passing tests prove CLI controller list/stat views match active nexus child controllers and show IO activity.
