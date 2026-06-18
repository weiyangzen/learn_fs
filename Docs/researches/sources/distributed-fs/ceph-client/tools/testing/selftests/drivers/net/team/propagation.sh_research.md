# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/propagation.sh

## Purpose
Exercises regressions in team lower-device feature and flag propagation: LRO propagation to a netdevsim lower, promiscuous flag propagation during enslave, and promiscuous propagation through `ndo_change_rx_flags` after the team is already up.

## Important APIs, Types, And Functions
The script uses `modprobe netdevsim`, `/sys/bus/netdevsim/new_device` and `del_device`, `ip link` team/dummy/macvlan operations, and `ethtool -K`. Local functions are `cleanup()`, `team_lro()`, `team_promisc()`, and `team_change_flags()`.

## Control Flow
With `set -e`, the script loads netdevsim, creates one simulated device, settles udev, then runs the three trigger functions. Each function builds the minimum topology needed to trigger propagation and deletes devices after the event. A trap tears down dummy/team devices, removes the simulator instance, and unloads netdevsim.

## State And Persistence
State is temporary netdevice/sysfs state. `NSIM_LRO_ID` randomizes the netdevsim id to avoid collisions. There is no persistent artifact.

## Dependencies And Integration Points
Requires root, netdevsim, team, dummy/macvlan, ethtool, udevadm, and writable netdevsim sysfs. It targets kernel team code paths linked in netdev mailing-list regressions.

## Risks
Because `set -e` is enabled, missing sysfs/debug support exits immediately. `modprobe netdevsim || :` permits a missing module until sysfs use fails. Random id collisions are unlikely but possible.

## Test Signals
The test is success-by-no-crash/no-command-failure. Relevant failures are command exit errors or kernel warnings around feature/flag propagation and lower-device lifetime.
