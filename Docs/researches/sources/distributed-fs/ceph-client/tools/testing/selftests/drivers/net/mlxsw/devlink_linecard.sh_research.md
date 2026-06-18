
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_linecard.sh`

## Purpose
Tests mlxsw devlink line card provisioning, unprovisioning, port instantiation, nested devlink information, and activation for a `16x100G` line card type.

## Important APIs, Types, And Functions
- State helpers `lc_state_get()`, `lc_wait_until_state_changes()`, `lc_wait_until_state_becomes()`, `lc_port_count_get()`, and `lc_nested_devlink_dev_get()` query devlink JSON through `jq`.
- `unprovision_one()` and `provision_one()` drive devlink line card state transitions.
- `supported_types_check()`, `ports_check()`, `lc_dev_info_provisioned_check()`, and `lc_dev_info_active_check()` validate metadata.
- Tests are `unprovision_test()`, `provision_test()`, and `activation_16x100G_test()`.

## Control Flow
`setup_prepare()` requires line card support and explicit `LC_SLOT`, then avoids creating netifs until activation. Tests unprovision/provision the selected slot, wait for expected states and port counts, read nested devlink device info, and for activation bring interfaces up before validating active firmware info.

## State And Persistence
Mutates physical line card provisioning state. Cleanup only brings test interfaces down if they were raised; it does not restore the previous line card type/state beyond what individual tests do.

## Dependencies And Integration Points
Depends on `devlink`, `jq`, forwarding `lib.sh`, `devlink_lib.sh`, an mlxsw platform with line card support, and `LC_SLOT` environment variable.

## Risks
This is disruptive to line card state and can take seconds to instantiate ports. It skips if `LC_SLOT` is absent, and `activation_16x100G_test()` is tied to a specific supported type.

## Test Signals
Pass requires successful devlink state transitions, expected provisioned type, exactly 16 ports for `16x100G`, nonempty nested devlink handle, and readable fixed/running firmware metadata.
