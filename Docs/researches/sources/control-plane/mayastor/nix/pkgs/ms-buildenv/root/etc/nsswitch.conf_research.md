# sources/control-plane/mayastor/nix/pkgs/ms-buildenv/root/etc/nsswitch.conf

Purpose: NSS lookup policy for the Mayastor build environment.

Important APIs/types/functions: configures `passwd` and `group` lookup through `files mymachines systemd`, `shadow` through `files`, `hosts` through `files mymachines dns myhostname`, and local files for networks/ethers/services/protocols/rpc.

Control flow: no script flow; glibc NSS uses the listed lookup order.

State/persistence: persistent rootfs configuration that affects name resolution and user/group lookup.

Dependencies/integration: supports local `/etc` files, systemd container users, and DNS resolution inside build/test environments.

Risks: DNS resolution depends on the runtime image having matching NSS modules. Lookup ordering can affect container hostnames and systemd-managed identities.

Test signals: build shell should resolve local users/groups and DNS hostnames without NSS errors.
