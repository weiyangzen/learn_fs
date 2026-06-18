# sources/distributed-fs/ceph-client/tools/hv/hv_set_ifconfig.sh

## Purpose

This shell script is the distro-specific network configuration hook invoked by `hv_kvp_daemon.c` after a host sends Hyper-V KVP IP configuration. The daemon writes an ifcfg-style file and a NetworkManager keyfile; this script installs them and cycles the target interface.

## Important APIs and Flow

The script appends `IPV6INIT=yes`, `NM_CONTROLLED=no`, `PEERDNS=yes`, and `ONBOOT=yes` to the first argument, copies that ifcfg file into `/etc/sysconfig/network-scripts/`, sets `umask 0177`, derives an interface name from the second argument with `awk -F - '{ print $2 }'`, inserts `autoconnect=true` after `[connection]`, writes the result to `/etc/NetworkManager/system-connections/<filename>`, then runs `/sbin/ifdown` and `/sbin/ifup` on the inferred interface.

## State, Dependencies, and Integration

The script mutates host guest network configuration in `/etc/sysconfig/network-scripts` and `/etc/NetworkManager/system-connections`. It assumes a RHEL-like system with legacy network scripts, NetworkManager keyfile support, `/sbin/ifdown`, `/sbin/ifup`, `sed`, `awk`, and root privileges. It is tightly coupled to `hv_kvp_daemon.c`, which supplies the two path arguments and expects persistent interface configuration after the script exits.

## Risks and Test Signals

Arguments are unquoted in several command positions, making spaces or shell metacharacters in generated paths unsafe. Interface derivation from `$2` with `-` as delimiter is fragile for arbitrary filenames and appears inconsistent with the daemon's `<ifname>.nmconnection` naming. The script appends to the ifcfg file each run, so repeated calls can duplicate keys. Tests should run it in a disposable rootfs or namespace with generated files, verify copied content and file permissions, and cover interface names with expected and unexpected formats.
