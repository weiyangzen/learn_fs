# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/dev_addr_lists.sh

Purpose: Tests that bonding updates underlying device address lists correctly, especially LACPDU multicast membership in different bond modes and carrier states.

Important APIs/functions: `destroy()`, `cleanup()`, `bond_cleanup_mode1()`, `bond_cleanup_mode4()`, `bond_listen_lacpdu_multicast()`, `bond_listen_lacpdu_multicast_case_down()`, `bond_listen_lacpdu_multicast_case_up()`, `ip maddr show`, bond modes 1 and 4, and test logging helpers.

Control flow: The script creates dummy devices and a bond, configures slaves, then checks multicast address list membership for LACPDU multicast under down/up cases and after cleanup. Separate cleanup paths account for active-backup and 802.3ad behavior.

State and persistence: Creates temporary dummy/bond devices and multicast memberships; cleanup deletes devices.

Dependencies and integration points: Requires bonding, dummy interfaces, multicast address inspection, and shell test helpers.

Risks and test signals: Failures point at leaked or missing hardware/multicast address list entries on slaves, especially after mode changes or link state transitions.
