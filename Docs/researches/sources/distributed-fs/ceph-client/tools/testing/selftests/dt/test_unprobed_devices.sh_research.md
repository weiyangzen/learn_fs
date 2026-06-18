# sources/distributed-fs/ceph-client/tools/testing/selftests/dt/test_unprobed_devices.sh

## Purpose
KTAP shell test that finds enabled devicetree nodes expected to bind to drivers and reports those without corresponding bound devices, excluding compatible strings in an ignore list.

## Important APIs, Types, And Functions
Uses `/proc/device-tree`, generated `compatible_list`, `compatible_ignore_list`, `/sys/devices/*/uevent` `OF_FULLNAME`, and `ktap_helpers.sh` functions such as `ktap_print_header`, `ktap_skip_all`, `ktap_set_plan`, `ktap_test_pass/fail/skip`, and `ktap_print_totals`.

## Control Flow
It skips if `/proc/device-tree` is absent. It builds `nodes_compatible` by walking enabled nodes with `compatible` properties while suppressing children of disabled ancestors. It builds `nodes_dev_bound` from devices with a driver and `OF_FULLNAME`. For each compatible node, it passes if bound, fails if any compatible appears in the generated compatible list and is not ignored, otherwise skips.

## State And Persistence
No state is modified. Variables hold derived node and device lists.

## Dependencies And Integration Points
Requires live devicetree, sysfs OF device names, generated compatible database, ignore list, and KTAP helpers.

## Risks
String matching uses whitespace-separated node paths and regex matching; unusual node names can affect matching. Missing compatible list entries turn unbound nodes into skips, not failures. Disabled ancestor regex can grow large.

## Test Signals
KTAP plan equals number of enabled compatible nodes. Per-node pass/fail/skip indicates binding status and whether the compatible is expected to have a driver.
